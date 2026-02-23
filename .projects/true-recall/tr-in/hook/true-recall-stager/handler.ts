import { HookHandler } from "@openclaw/hooks";
import { spawn } from "child_process";
import * as path from "path";

const STAGE_SCRIPT = path.join(
  process.env.HOME || "/root",
  ".openclaw/workspace/skills/true-recall-out/scripts/stage_turn.py"
);

const handler: HookHandler = async (event) => {
  // Only process sent messages (AI responses)
  if (event.action !== "sent") return;
  
  const { content, channelId, conversationId } = event.context;
  
  // Get the inbound user message from context
  // OpenClaw should provide this in the event context
  const userMessage = event.context.inboundContent || "";
  
  // Skip if no user message (shouldn't happen, but safety check)
  if (!userMessage.trim()) return;
  
  // Call stage_turn.py to buffer to Redis
  return new Promise((resolve) => {
    const proc = spawn("python3", [
      STAGE_SCRIPT,
      "--user-id", "USER_ID",
      "--user-msg", userMessage,
      "--ai-response", content || "",
      "--turn", Date.now().toString()
    ], {
      detached: true,
      stdio: "ignore"
    });
    
    proc.unref();
    resolve();
  });
};

export default handler;
