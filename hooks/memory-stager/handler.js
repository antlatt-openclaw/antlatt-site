var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);
var handler_exports = {};
__export(handler_exports, {
  default: () => handler_default
});
module.exports = __toCommonJS(handler_exports);
var import_child_process = require("child_process");
var fs = __toESM(require("fs"));
const REDIS_HOST = process.env.REDIS_HOST || "192.168.1.206";
const REDIS_PORT = process.env.REDIS_PORT || "6379";
const LOG_FILE = "/tmp/memory-stager.log";
function log(msg) {
  const ts = (/* @__PURE__ */ new Date()).toISOString();
  const line = `[${ts}] ${msg}
`;
  console.log(`[memory-stager] ${msg}`);
  try {
    fs.appendFileSync(LOG_FILE, line);
  } catch (e) {
  }
}
const turnCounter = /* @__PURE__ */ new Map();
async function stageTurn(userId, userMsg, aiResponse, channelId, sessionId, conversationId) {
  const now = /* @__PURE__ */ new Date();
  const timestamp = now.toISOString();
  const date = now.toISOString().split("T")[0];
  const turn = (turnCounter.get(conversationId) || 0) + 1;
  turnCounter.set(conversationId, turn);
  const turnData = {
    user_id: userId,
    user_message: userMsg,
    ai_response: aiResponse,
    turn,
    timestamp,
    date,
    conversation_id: conversationId,
    channel: channelId
  };
  const turnB64 = Buffer.from(JSON.stringify(turnData)).toString("base64");
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
    const proc = (0, import_child_process.spawn)("python3", ["-c", pythonCode]);
    let stdout = "", stderr = "";
    proc.stdout.on("data", (d) => stdout += d);
    proc.stderr.on("data", (d) => stderr += d);
    proc.on("close", (code) => {
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
async function updateTurnWithResponse(userId, aiResponse) {
  const aiResponseB64 = Buffer.from(aiResponse).toString("base64");
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
    const proc = (0, import_child_process.spawn)("python3", ["-c", pythonCode]);
    let stdout = "", stderr = "";
    proc.stdout.on("data", (d) => stdout += d);
    proc.stderr.on("data", (d) => stderr += d);
    proc.on("close", (code) => {
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
const pendingUserMsgs = /* @__PURE__ */ new Map();
const sessionToConversation = /* @__PURE__ */ new Map();
async function handleMessageEvent(event) {
  log(`Message event: action=${event.action}`);
  const { action, context, sessionKey } = event;
  const conversationId = context.conversationId || sessionKey;
  const content = context.content || "";
  sessionToConversation.set(sessionKey, conversationId);
  if (action === "received") {
    if (!content.trim()) return;
    const pending = pendingUserMsgs.get(conversationId);
    if (pending && Date.now() - pending.timestamp < 5e3) {
      log(`Skipping duplicate within 5s`);
      return;
    }
    try {
      const turnNumber = await stageTurn(
        "antlatt",
        content,
        "",
        // AI response empty for now
        context.channelId || "unknown",
        sessionKey,
        conversationId
      );
      pendingUserMsgs.set(conversationId, {
        userMsg: content,
        channelId: context.channelId || "unknown",
        sessionId: sessionKey,
        conversationId,
        timestamp: Date.now(),
        turnNumber
      });
    } catch (err) {
      log(`Stage failed: ${err}`);
    }
  }
  if (action === "sent") {
    if (!content.trim()) {
      log(`Sent event with empty content, skipping`);
      return;
    }
    try {
      await updateTurnWithResponse("antlatt", content);
      log(`Got SENT event, updated turn with response`);
    } catch (err) {
      log(`Failed to update turn with AI response: ${err}`);
    }
    pendingUserMsgs.delete(conversationId);
  }
}
async function handleLlmOutputEvent(event) {
  const { sessionKey, context } = event;
  const assistantTexts = context?.assistantTexts || [];
  log(`LLM output event: sessionKey=${sessionKey}, texts=${assistantTexts.length}`);
  const conversationId = sessionToConversation.get(sessionKey) || sessionKey;
  const content = assistantTexts.join("\n").trim();
  if (!content) {
    log(`LLM output with empty content, skipping`);
    return;
  }
  try {
    await updateTurnWithResponse("antlatt", content);
    log(`Updated turn with LLM output (${content.length} chars)`);
  } catch (err) {
    log(`Failed to update turn with LLM output: ${err}`);
  }
  pendingUserMsgs.delete(conversationId);
}
const handler = async (event) => {
  if (event.type === "message") {
    await handleMessageEvent(event);
  } else if (event.type === "llm" && event.action === "output") {
    await handleLlmOutputEvent(event);
  } else {
    log(`Unknown event structure: type=${event.type}, action=${event.action}`);
  }
};
var handler_default = handler;
