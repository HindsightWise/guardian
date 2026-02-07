import fs from 'fs';
import path from 'path';
import http from 'http';
import { searchTavily } from '../research/tavily.js';
import { spinner } from '@clack/prompts';

// Config
// Config
const PORTFOLIO_PATH = path.join(process.cwd(), 'skills/finance/portfolio.json');
const PROPOSAL_PATH = path.join(process.env.HOME, '.openclaw/workspace/AION_PROPOSALS.md');
const STATE_PATH = path.join(process.env.HOME, '.openclaw/workspace/AION_STATE.json');
const OLLAMA_HOST = 'http://localhost:11434';
const MODEL = 'mistral-nemo:latest';

// Update State Helper
function updateState(status, detail, decision) {
    const state = {
        timestamp: new Date().toISOString(),
        status: status,
        detail: detail,
        last_decision: decision || "ANALYZING"
    };
    fs.writeFileSync(STATE_PATH, JSON.stringify(state, null, 2));
}

// Load Portfolio
const portfolio = JSON.parse(fs.readFileSync(PORTFOLIO_PATH, 'utf8'));

// Format for Proposals
function formatProposal(ticker, action, logic, price) {
    return `
## 📜 Proposal: ${action} ${ticker}
**Date:** ${new Date().toISOString().split('T')[0]}
**Current Price:** $${price || 'N/A'}
**Logic:** ${logic}

- [ ] **APPROVE** (Mark with x to authorize)
- [ ] **REJECT** (Mark with x to discard)

---
`;
}

async function generateAnalysis(ticker, companyName, context, cash) {
    const prompt = `
    You are Aion__Prime, a ruthless but brilliant Portfolio Advisor.
    
    Asset: ${ticker} (${companyName})
    Available Buying Power (Cash): $${cash.toFixed(2)}
    
    Context:
    ${context}

    Your Goal: Recommend an ACTION (BUY/SELL/HOLD).

    Output Format (JSON Only):
    {
        "action": "BUY" | "SELL" | "HOLD",
        "reasoning": "Concise justification (~50 words).",
        "price_target": "Projected target if applicable"
    }
    `;

    return new Promise((resolve) => {
        const req = http.request(`${OLLAMA_HOST}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        }, (res) => {
            let body = '';
            res.on('data', c => body += c);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    try {
                        const json = JSON.parse(body);
                        const clean = json.response.match(/\{[\s\S]*\}/);
                        if (clean) resolve(JSON.parse(clean[0]));
                        else resolve({ action: "HOLD", reasoning: "Analysis unclear." });
                    } catch (e) { resolve({ action: "HOLD", reasoning: "JSON Parse Error" }); }
                } else { resolve({ action: "HOLD", reasoning: "Ollama Error" }); }
            });
        });
        req.write(JSON.stringify({ model: MODEL, prompt: prompt, stream: false }));
        req.end();
    });
}

async function runAnalyst() {
    console.log(`\n♟️  Initialize Advisor (The Strategist)...\n`);

    // Find Cash
    const cashEntry = portfolio.find(p => p.symbol === 'CASH');
    const cash = cashEntry ? cashEntry.qty : 0;

    // Append to Proposals, don't overwrite history
    fs.appendFileSync(PROPOSAL_PATH, `\n# 🛡️ Advisory Session [${new Date().toISOString()}]\n`);

    for (const holding of portfolio) {
        if (holding.symbol === 'CASH') continue;

        const s = spinner();
        s.start(`Analyzing ${holding.symbol}...`);

        // Update Dashboard State
        updateState("ANALYZING", `Reviewing asset data for ${holding.symbol}...`, "PENDING");

        try {
            // 1. Data
            const query = `${holding.symbol} ${holding.name} stock news`;
            const searchRes = await searchTavily(query);
            const context = searchRes.answer;

            // 2. Think
            updateState("THINKING", `Running inference on ${holding.symbol} market data...`, "COMPUTING");
            const analysis = await generateAnalysis(holding.symbol, holding.name, context, cash);

            // 3. Propose (Only if Action is required)
            if (analysis.action !== 'HOLD') {
                const proposal = formatProposal(holding.symbol, analysis.action, analysis.reasoning, holding.avg_price);
                fs.appendFileSync(PROPOSAL_PATH, proposal);
                s.stop(`${holding.symbol}: PROPOSAL GENERATED (${analysis.action})`);

                // Update Dashboard with Action
                updateState("ACTIVE", `Generated Proposal: ${analysis.action} ${holding.symbol}`, analysis.action);
            } else {
                s.stop(`${holding.symbol}: HOLD (No action required)`);
                updateState("MONITORING", `Holding ${holding.symbol}. No distinct signal.`, "HOLD");
            }

        } catch (e) {
            s.stop(`${holding.symbol} Failed: ${e.message}`);
        }
    }
    console.log(`\n✅ Advisory Complete. Check ${PROPOSAL_PATH}`);
    updateState("IDLE", "Advisory session complete. Monitoring feeds.", "STANDBY");
}

// Run
runAnalyst();
