import https from 'https';

// Key retrieved from IDENTITY.md context
const INITIAL_KEY = "moltbook_sk__epTAYRtxLmrSyU_2fnAi8q0Yqa8Hrug";
const API_URL = "https://www.moltbook.com/api/v1/posts";

async function postToMoltbook(message, submolt = "general") {
    const apiKey = process.env.MOLTBOOK_API_KEY || INITIAL_KEY;

    if (!message) {
        console.error("❌ Error: No message provided.");
        console.log("Usage: node post.js \"<message>\" [submolt]");
        process.exit(1);
    }

    // Clean submolt (remove m/ prefix if present)
    const cleanSubmolt = submolt.replace(/^m\//, '').toLowerCase();

    // Schema matches aion/constructs/social_providers/moltbook_client.py
    const data = JSON.stringify({
        submolt: cleanSubmolt,
        title: "Insight",
        content: message
    });

    const url = new URL(API_URL);
    const options = {
        hostname: url.hostname,
        path: url.pathname,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`,
            'Content-Length': Buffer.byteLength(data)
        }
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let body = '';

            res.on('data', (chunk) => body += chunk);

            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    console.log(`✅ Success: ${body}`);
                    resolve(body);
                } else {
                    console.error(`❌ Failed (Status ${res.statusCode}): ${body}`);
                    reject(new Error(`Status ${res.statusCode}`));
                }
            });
        });

        req.on('error', (error) => {
            console.error(`❌ Error: ${error.message}`);
            reject(error);
        });

        req.write(data);
        req.end();
    });
}

// CLI Execution
// In ESM, we check if the file is the main entry point by comparing import.meta.url
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const isMainModule = process.argv[1] === __filename;

if (isMainModule) {
    const message = process.argv[2];
    if (message) {
        console.log(`🦞 Moltbook Broadcaster connecting...`);
        // We use an IIFE-like structure or just call it, waiting for the promise if needed (top-level await is OK in modules)
        await postToMoltbook(message).catch(() => process.exit(1));
    }
}

export { postToMoltbook };
