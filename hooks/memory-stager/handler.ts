import { spawn } from 'child_process';
import * as fs from 'fs';

// Redis config from env
const REDIS_HOST = process.env.REDIS_HOST || '192.168.1.206';
const REDIS_PORT = process.env.REDIS_PORT || '6379';

// Debug log file
const LOG_FILE = '/tmp/memory-stager.log';

function log(msg: string) {
  const ts = new Date().toISOString();
  const line = `[${ts}] ${msg}\n`;
  console.log(`[memory-stager] ${msg}`);
  try {
    fs.appendFileSync(LOG_FILE, line);
  } catch (e) {}
}

// Message hook event (message:received, message:sent)
interface MessageHookEvent {
  type: 'message';
  action: 'received' | 'sent';
  sessionKey: string;
  timestamp: Date;
  messages: string[];
  context: {
    from?: string;
    to?: string;
    content?: string;
    channelId?: string;
    accountId?: string;
    conversationId?: string;
    messageId?: string;
    success?: boolean;
    metadata?: Record<string, unknown>;
  };
}

// LLM output hook event (internal hook: llm:output)
interface LlmOutputEvent {
  type: 'llm';
  action: 'output';
  sessionKey: string;
  timestamp: Date;
  context: {
    runId: string;
    sessionId: string;
    provider: string;
    model: string;
    assistantTexts: string[];
    usage?: {
      input?: number;
      output?: number;
      cacheRead?: number;
      cacheWrite?: number;
      total?: number;
    };
  };
}

// Track turn number globally (per conversation)
const turnCounter: Map<string, number> = new Map();

async function stageTurn(userId: string, userMsg: string, aiResponse: string, channelId: string, sessionId: string, conversationId: string): Promise<number> {
  const now = new Date();
  const timestamp = now.toISOString();
  const date = now.toISOString().split('T')[0];
  
  // Get/increment turn counter for this conversation
  const turn = (turnCounter.get(conversationId) || 0) + 1;
  turnCounter.set(conversationId, turn);
  
  // Create complete turn matching curator's expected format
  const turnData = {
    user_id: userId,
    user_message: userMsg,
    ai_response: aiResponse,
    turn: turn,
    timestamp: timestamp,
    date: date,
    conversation_id: conversationId,
    channel: channelId
  };
  
  const turnB64 = Buffer.from(JSON.stringify(turnData)).toString('base64');
  
  const pythonCode = `
import json
import redis
import base64
r = redis.Redis(host='${REDIS_HOST}', port=${REDIS_PORT}, decode_responses=True)
turn = json.loads(base64.b64decode('${turnB64}').decode('utf-8'))
r.rpush('mem:${userId}', json.dumps(turn))
print(f"Staged turn {turn['turn']} to mem:${userId}")
`;
  
  return new Promise((resolve, reject) => {
    const proc = spawn('python3', ['-c', pythonCode]);
    let stdout = '', stderr = '';
    proc.stdout.on('data', (d) => stdout += d);
    proc.stderr.on('data', (d) => stderr += d);
    proc.on('close', (code) => {
      if (code === 0) {
        log(`Staged turn ${turn}: ${userMsg.slice(0, 40)}...`);
        resolve(turn);
      } else {
        log(`Error: ${stderr}`);
        reject(new Error(stderr));
      }
    });
  });
}

async function updateTurnWithResponse(userId: string, aiResponse: string): Promise<void> {
  const aiResponseB64 = Buffer.from(aiResponse).toString('base64');
  
  const pythonCode = `
import json
import redis
import base64

r = redis.Redis(host='${REDIS_HOST}', port=${REDIS_PORT}, decode_responses=True)

# Get the last turn
last_turn_json = r.lindex('mem:${userId}', -1)
if not last_turn_json:
    print("No turns found to update")
    exit(1)

# Parse, update ai_response, save back
turn = json.loads(last_turn_json)
turn['ai_response'] = base64.b64decode('${aiResponseB64}').decode('utf-8')
r.lset('mem:${userId}', -1, json.dumps(turn))
print(f"Updated turn {turn.get('turn', '?')} with AI response")
`;
  
  return new Promise((resolve, reject) => {
    const proc = spawn('python3', ['-c', pythonCode]);
    let stdout = '', stderr = '';
    proc.stdout.on('data', (d) => stdout += d);
    proc.stderr.on('data', (d) => stderr += d);
    proc.on('close', (code) => {
      if (code === 0) {
        log(`Updated turn with AI response: ${aiResponse.slice(0, 40)}...`);
        resolve();
      } else {
        log(`Failed to update turn: ${stderr}`);
        reject(new Error(stderr));
      }
    });
  });
}

// Pending messages waiting for AI response
interface PendingMsg {
  userMsg: string;
  channelId: string;
  sessionId: string;
  conversationId: string;
  timestamp: number;
  turnNumber: number;
}
const pendingUserMsgs: Map<string, PendingMsg> = new Map();

// Track session ID to conversation ID mapping
const sessionToConversation: Map<string, string> = new Map();

// Message hook handler (for message:received, message:sent events)
async function handleMessageEvent(event: MessageHookEvent) {
  log(`Message event: action=${event.action}`);
  
  const { action, context, sessionKey } = event;
  const conversationId = context.conversationId || sessionKey;
  const content = context.content || '';
  
  // Track session -> conversation mapping for llm_output events
  sessionToConversation.set(sessionKey, conversationId);
  
  if (action === 'received') {
    // User message - stage immediately (don't wait for AI response)
    if (!content.trim()) return;
    
    // Check if we have a pending message (avoid duplicates)
    const pending = pendingUserMsgs.get(conversationId);
    if (pending && Date.now() - pending.timestamp < 5000) {
      log(`Skipping duplicate within 5s`);
      return;
    }
    
    try {
      const turnNumber = await stageTurn(
        'antlatt',
        content,
        '', // AI response empty for now
        context.channelId || 'unknown',
        sessionKey,
        conversationId
      );
      // Mark as pending so we can update when AI responds
      pendingUserMsgs.set(conversationId, {
        userMsg: content,
        channelId: context.channelId || 'unknown',
        sessionId: sessionKey,
        conversationId: conversationId,
        timestamp: Date.now(),
        turnNumber: turnNumber
      });
    } catch (err) {
      log(`Stage failed: ${err}`);
    }
  }
  
  if (action === 'sent') {
    // AI response - update the most recent turn (fallback)
    if (!content.trim()) {
      log(`Sent event with empty content, skipping`);
      return;
    }
    
    try {
      await updateTurnWithResponse('antlatt', content);
      log(`Got SENT event, updated turn with response`);
    } catch (err) {
      log(`Failed to update turn with AI response: ${err}`);
    }
    
    // Clean up pending
    pendingUserMsgs.delete(conversationId);
  }
}

// LLM output hook handler
async function handleLlmOutputEvent(event: LlmOutputEvent) {
  const { sessionKey, context } = event;
  const assistantTexts = context?.assistantTexts || [];
  
  log(`LLM output event: sessionKey=${sessionKey}, texts=${assistantTexts.length}`);
  
  const conversationId = sessionToConversation.get(sessionKey) || sessionKey;
  
  const content = assistantTexts.join('\n').trim();
  if (!content) {
    log(`LLM output with empty content, skipping`);
    return;
  }
  
  try {
    await updateTurnWithResponse('antlatt', content);
    log(`Updated turn with LLM output (${content.length} chars)`);
  } catch (err) {
    log(`Failed to update turn with LLM output: ${err}`);
  }
  
  // Clean up pending
  pendingUserMsgs.delete(conversationId);
}

// Main handler - exports for different hook types
const handler = async (event: any) => {
  // Determine event type and route accordingly
  if (event.type === 'message') {
    // Message hook (message:received, message:sent)
    await handleMessageEvent(event);
  } else if (event.type === 'llm' && event.action === 'output') {
    // LLM output hook (llm:output)
    await handleLlmOutputEvent(event);
  } else {
    log(`Unknown event structure: type=${event.type}, action=${event.action}`);
  }
};

export default handler;