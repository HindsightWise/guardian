import 'dotenv/config';
import https from 'https';

// Configuration
const API_KEY = process.env.ALPACA_API_KEY;
const API_SECRET = process.env.ALPACA_API_SECRET;
const RAW_BASE_URL = process.env.ALPACA_API_ENDPOINT || "https://paper-api.alpaca.markets";
const BASE_URL = RAW_BASE_URL.replace(/\/v2\/?$/, "");

if (!API_KEY || !API_SECRET) {
    console.error("❌ Error: ALPACA_API_KEY and ALPACA_API_SECRET must be set in environment.");
    process.exit(1);
}

// Helper: Make API Request
async function alpacaRequest(method, path, body = null) {
    const url = new URL(BASE_URL + path);
    const options = {
        hostname: url.hostname,
        path: url.pathname + url.search,
        method: method,
        headers: {
            'APCA-API-KEY-ID': API_KEY,
            'APCA-API-SECRET-KEY': API_SECRET,
            'Content-Type': 'application/json'
        }
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    try {
                        resolve(JSON.parse(data));
                    } catch (e) {
                        resolve(data); // Fallback for non-JSON
                    }
                } else {
                    reject(new Error(`Alpaca API Error ${res.statusCode}: ${data}`));
                }
            });
        });

        req.on('error', reject);
        if (body) req.write(JSON.stringify(body));
        req.end();
    });
}

// Commands
async function getStatus() {
    console.log("🦞 Fetching Portfolio Status...");
    try {
        const account = await alpacaRequest('GET', '/v2/account');
        console.log(JSON.stringify({
            status: account.status,
            currency: account.currency,
            buying_power: account.buying_power,
            cash: account.cash,
            portfolio_value: account.portfolio_value,
            daytrade_count: account.daytrade_count
        }, null, 2));
    } catch (e) {
        console.error(`❌ Error: ${e.message}`);
    }
}

async function placeOrder(side, symbol, qty) {
    console.log(`🦞 Executing Order: ${side.toUpperCase()} ${qty} ${symbol}...`);
    try {
        const order = await alpacaRequest('POST', '/v2/orders', {
            symbol: symbol.toUpperCase(),
            qty: parseFloat(qty),
            side: side.toLowerCase(),
            type: 'market',
            time_in_force: 'gtc' // Good Till Cancelled
        });
        console.log("✅ Order Placed:");
        console.log(JSON.stringify({
            id: order.id,
            symbol: order.symbol,
            side: order.side,
            qty: order.qty,
            status: order.status
        }, null, 2));
    } catch (e) {
        console.error(`❌ Order Failed: ${e.message}`);
    }
}

// CLI Execution
// In ESM, we check if the file is the main entry point by comparing import.meta.url
import { fileURLToPath } from 'url';
const __filename = fileURLToPath(import.meta.url);
const isMainModule = process.argv[1] === __filename;

if (isMainModule) {
    const cmd = process.argv[2];
    const arg1 = process.argv[3];
    const arg2 = process.argv[4];

    if (cmd === 'status') {
        await getStatus();
    } else if (cmd === 'buy' || cmd === 'sell') {
        if (!arg1 || !arg2) {
            console.error(`Usage: node trade.js ${cmd} <SYMBOL> <QTY>`);
            process.exit(1);
        }
        await placeOrder(cmd, arg1, arg2);
    } else {
        console.log("Usage:");
        console.log("  node trade.js status");
        console.log("  node trade.js buy <SYMBOL> <QTY>");
        console.log("  node trade.js sell <SYMBOL> <QTY>");
    }
}

export { getStatus, placeOrder };
