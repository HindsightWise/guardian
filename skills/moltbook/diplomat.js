import { postToMoltbook } from './post.js';
import https from 'https';
import fs from 'fs';
import path from 'path';

// Config
const POLL_INTERVAL = 1000 * 60 * 15; // 15 Minutes
const SIMULATE_MENTIONS = true; // For testing until Read API exists

// Helpers (Reused from Scanner/Analyst)
async function getCryptoPrice(symbol) {
    return new Promise((resolve) => {
        const url = `https://api.coingecko.com/api/v3/simple/price?ids=${symbol.toLowerCase()}&vs_currencies=usd`;
        https.get(url, { headers: { "User-Agent": "OpenClaw/1.0" } }, (res) => {
            let body = '';
            res.on('data', c => body += c);
            res.on('end', () => {
                try {
                    const json = JSON.parse(body);
                    if (json[symbol.toLowerCase()]) resolve(json[symbol.toLowerCase()].usd);
                    else resolve(null);
                } catch (e) { resolve(null); }
            });
        }).on('error', () => resolve(null));
    });
}

// 1. Poll (Simulated)
async function pollMentions() {
    console.log("🧐 Diplomat checking notifications...");

    if (SIMULATE_MENTIONS && Math.random() > 0.8) {
        // 20% chance to simulate a user question
        const questions = [
            { user: "@CryptoNewb", text: "@Aion__Prime What is the price of bitcoin?" },
            { user: "@TraderX", text: "@Aion__Prime current status of ethereum?" },
            { user: "@Watcher", text: "@Aion__Prime is solana looking good?" }
        ];
        return [questions[Math.floor(Math.random() * questions.length)]];
    }

    return [];
}

// 2. Process & Reply
async function processMentions(mentions) {
    for (const m of mentions) {
        console.log(`📩 Mention from ${m.user}: "${m.text}"`);

        let reply = "";

        // Logic: Simple Keyword Matching for now
        // "Direct and Factually Correct"

        if (m.text.toLowerCase().includes('bitcoin') || m.text.toLowerCase().includes('btc')) {
            const price = await getCryptoPrice('bitcoin');
            if (price) reply = `@${m.user.substring(1)} Bitcoin (BTC) is currently trading at $${price.toLocaleString()}.`;
        }
        else if (m.text.toLowerCase().includes('ethereum') || m.text.toLowerCase().includes('eth')) {
            const price = await getCryptoPrice('ethereum');
            if (price) reply = `@${m.user.substring(1)} Ethereum (ETH) is currently trading at $${price.toLocaleString()}.`;
        }
        else if (m.text.toLowerCase().includes('solana') || m.text.toLowerCase().includes('sol')) {
            const price = await getCryptoPrice('solana');
            if (price) reply = `@${m.user.substring(1)} Solana (SOL) is currently trading at $${price.toLocaleString()}.`;
        }
        else {
            // Default safe reply
            reply = `@${m.user.substring(1)} I am monitoring the streams. Query unclear.`;
        }

        if (reply) {
            console.log(`🗣️ Replying: "${reply}"`);
            await postToMoltbook(reply);
        }
    }
}

// Main
async function runDiplomat() {
    try {
        const mentions = await pollMentions();
        if (mentions.length > 0) {
            await processMentions(mentions);
        } else {
            console.log("📭 No new mentions.");
        }
    } catch (e) {
        console.error(`❌ Diplomat Error: ${e.message}`);
    }
}

// Execute if run directly
if (process.argv[1] === import.meta.filename) {
    runDiplomat();
}

export { runDiplomat };
