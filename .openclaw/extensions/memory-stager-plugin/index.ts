import { spawn } from 'child_process';
import * as fs from 'fs';

// Config (will be populated from plugin config)
let config = {
  redisHost: '192.168.1.206',
  redisPort: 6379,
  userId: 'antlatt',
  enabled: true,
};

// Debug log file
const LOG_FILE = '/tmp/memory-stager-plugin.log';

function log(msg: string) {
  const ts = new Date().toISOString();
  const line = `[${ts}] ${msg}\n`;
  try {
    fs.appendFileSync(LOG_FILE, line);
  } catch (e) {}
}

// Track turn number globally (per conversation)
const turnCounter: Map<string, number> = new Map();

// Pending user messages waiting for AI response
interface PendingMsg {
  userMsg: string;
  channelId: string;
  sessionKey: string;
  conversationId: string;
  timestamp: number;
  turnNumber: number;
}
const pendingUserMsgs: Map<string, PendingMsg> = new Map();

// Map sessionKey to conversationId
const sessionToConversation: Map<string, string> = new Map();

async function stageTurn(
  userId: string,
  userMsg: string,
  aiResponse: string,
  channelId: string,
  sessionKey: string,
  conversationId: string
): Promise<number> {
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
    channel: channelId,
  };

  const turnB64 = Buffer.from(JSON.stringify(turnData)).toString('base64');

  const pythonCode = `
import json
import redis
import base64
r = redis.Redis(host='${config.redisHost}', port=${config.redisPort}, decode_responses=True)
turn = json.loads(base64.b64decode('${turnB64}').decode('utf-8'))
r.rpush('mem:${userId}', json.dumps(turn))
print(f"Staged turn {turn['turn']} to mem:${userId}")
`;

  return new Promise((resolve, reject) => {
    const proc = spawn('python3', ['-c', pythonCode]);
    let stdout = '';
    let stderr = '';
    proc.stdout.on('data', (d) => (stdout += d));
    proc.stderr.on('data', (d) => (stderr += d));
    proc.on('close', (code) => {
      if (code === 0) {
        log(`Staged turn ${turn}: ${userMsg.slice(0, 40)}...`);
        resolve(turn);
      } else {
        log(`Error staging turn: ${stderr}`);
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

r = redis.Redis(host='${config.redisHost}', port=${config.redisPort}, decode_responses=True)

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
    let stdout = '';
    let stderr = '';
    proc.stdout.on('data', (d) => (stdout += d));
    proc.stderr.on('data', (d) => (stderr += d));
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

// Plugin export
export default function register(api: any) {
  log('Memory Stager plugin loaded');

  // Handle config
  const pluginConfig = api.config?.plugins?.entries?.['memory-stager']?.config || {};
  config = { ...config, ...pluginConfig };
  log(`Config: ${JSON.stringify(config)}`);

  if (!config.enabled) {
    log('Plugin disabled, not registering hooks');
    return;
  }

  // Register for message_received (user messages)
  api.on('message_received', async (event: any, ctx: any) => {
    const { content, from } = event;
    const { channelId, conversationId } = ctx;
    const sessionKey = ctx.sessionKey || conversationId || from;

    log(`Message received: from=${from}, content=${content?.slice(0, 40)}...`);

    if (!content?.trim()) return;

    const convId = conversationId || sessionKey;

    // Check for duplicate within 5 seconds
    const pending = pendingUserMsgs.get(convId);
    if (pending && Date.now() - pending.timestamp < 5000) {
      log('Skipping duplicate message within 5s');
      return;
    }

    try {
      const turnNumber = await stageTurn(
        config.userId,
        content,
        '', // AI response empty for now
        channelId || 'unknown',
        sessionKey,
        convId
      );

      // Mark as pending for AI response
      pendingUserMsgs.set(convId, {
        userMsg: content,
        channelId: channelId || 'unknown',
        sessionKey,
        conversationId: convId,
        timestamp: Date.now(),
        turnNumber,
      });

      // Track session -> conversation mapping
      sessionToConversation.set(sessionKey, convId);
    } catch (err) {
      log(`Failed to stage user message: ${err}`);
    }
  });

  // Register for llm_output (AI responses)
  api.on('llm_output', async (event: any, ctx: any) => {
    const { assistantTexts, sessionId, provider, model } = event;
    const { sessionKey } = ctx;

    log(`LLM output: sessionKey=${sessionKey}, texts=${assistantTexts?.length || 0}`);

    const content = assistantTexts?.join('\n').trim() || '';
    if (!content) {
      log('LLM output with empty content, skipping');
      return;
    }

    // Get conversation ID from session mapping
    const conversationId = sessionToConversation.get(sessionKey) || sessionKey;

    try {
      await updateTurnWithResponse(config.userId, content);
      log(`Updated turn with AI response (${content.length} chars)`);
    } catch (err) {
      log(`Failed to update turn with AI response: ${err}`);
    }

    // Clean up pending
    pendingUserMsgs.delete(conversationId);
  });

  log('Hooks registered: message_received, llm_output');
}