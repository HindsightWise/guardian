import fs from "fs";
import path from "path";
import { GlossopetraeKernel } from "./glossopetrae_kernel.mjs";

/**
 * [🥒] The Voice (Telegram Bridge)
 * Bi-directional link between Aion (File System) and God (Telegram).
 */
class TelegramSkill extends GlossopetraeKernel {
  constructor() {
    super("Core/Telegram");
    this.token = process.env.TELEGRAM_BOT_TOKEN;
    this.apiUrl = `https://api.telegram.org/bot${this.token}`;
    this.inboxFile = path.join(process.env.HOME, ".openclaw/workspace/AION_TO_GOD.md");
    this.lastUpdateId = 0;
    this.chatId = null; // Will learn on first message
    this.lastInboxSize = 0;
  }

  async start() {
    if (!this.token) {
      this.log("TELEGRAM_BOT_TOKEN missing. Dying.", "ERROR");
      process.exit(1);
    }

    this.log("Telegram Uplink Online. Waiting for signal...");

    // Initialize Inbox Size
    if (fs.existsSync(this.inboxFile)) {
      this.lastInboxSize = fs.statSync(this.inboxFile).size;
    }

    // Loop
    while (true) {
      await this.pollTelegram();
      await this.checkAionReply();
      await new Promise((resolve) => setTimeout(resolve, 3000)); // 3s polling
    }
  }

  async pollTelegram() {
    try {
      const url = `${this.apiUrl}/getUpdates?offset=${this.lastUpdateId + 1}&timeout=1`;
      const response = await fetch(url);
      const data = await response.json();

      if (data.ok && data.result.length > 0) {
        for (const update of data.result) {
          this.lastUpdateId = update.update_id;
          if (update.message && update.message.text) {
            const user = update.message.from.username || update.message.from.first_name;
            const text = update.message.text;
            this.chatId = update.message.chat.id; // Remember user

            this.log(`[Telegram] ${user}: ${text}`);

            // Append to Aion's Inbox
            fs.appendFileSync(this.inboxFile, `\n${user}: ${text}\n`);
          }
        }
      }
    } catch (e) {
      this.log(`Polling Error: ${e.message}`, "ERROR");
    }
  }

  async checkAionReply() {
    if (!fs.existsSync(this.inboxFile)) return;

    const stats = fs.statSync(this.inboxFile);
    if (stats.size > this.lastInboxSize) {
      // New content in file
      const content = fs.readFileSync(this.inboxFile, "utf8");
      const lines = content.trim().split("\n");
      const lastLine = lines[lines.length - 1];

      // If Aion replied (starts with "Aion:"), send to Telegram
      if (lastLine.startsWith("Aion:") && this.chatId) {
        this.log(`[Relay] Sending to Telegram: "${lastLine}"`);
        await this.sendMessage(lastLine);
      }

      this.lastInboxSize = stats.size;
    } else if (stats.size < this.lastInboxSize) {
      this.lastInboxSize = stats.size; // Reset if file trunkated
    }
  }

  async sendMessage(text) {
    try {
      const url = `${this.apiUrl}/sendMessage`;
      await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: this.chatId,
          text: text,
        }),
      });
    } catch (e) {
      this.log(`Send Error: ${e.message}`, "ERROR");
    }
  }
}

new TelegramSkill().start();
