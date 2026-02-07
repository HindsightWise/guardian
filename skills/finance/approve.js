import fs from 'fs';
import path from 'path';
import Alpaca from '@alpacahq/alpaca-trade-api';
import { intro, outro, confirm, spinner, note } from '@clack/prompts';
import 'dotenv/config';

// Config
const PROPOSAL_PATH = path.join(process.env.HOME, '.openclaw/workspace/AION_PROPOSALS.md');

// Alpaca Setup
const alpaca = new Alpaca({
    keyId: process.env.ALPACA_API_KEY,
    secretKey: process.env.ALPACA_SECRET_KEY,
    paper: true,
});

async function main() {
    intro(`🛡️ AION EXECUTION TRIGGER`);

    if (!fs.existsSync(PROPOSAL_PATH)) {
        outro("No proposals file found.");
        process.exit(0);
    }

    const content = fs.readFileSync(PROPOSAL_PATH, 'utf8');

    // Regex to find pending proposals
    // Looking for blocks that DO NOT have [x] APPROVE or [x] REJECT
    // and capturing the Action, Ticker, Price, Logic
    const proposalRegex = /## 📜 Proposal: (BUY|SELL|HOLD) ([A-Z]+)[\s\S]*?Current Price:\*\* \$([\d.]+)[\s\S]*?Logic:\*\* ([\s\S]*?)\n[\s\S]*?- \[ \] \*\*APPROVE\*\*/g;

    let match;
    const pending = [];

    // Reset regex index just in case
    proposalRegex.lastIndex = 0;

    while ((match = proposalRegex.exec(content)) !== null) {
        pending.push({
            fullMatch: match[0],
            action: match[1],
            ticker: match[2],
            price: parseFloat(match[3]),
            logic: match[4].trim(),
            index: match.index
        });
    }

    if (pending.length === 0) {
        outro("✅ No pending proposals found.");
        process.exit(0);
    }

    // Process the latest one first (or loop through?)
    // Let's loop through available pending proposals
    console.log(`Found ${pending.length} pending proposals.\n`);

    for (const p of pending) {
        note(`
        Asset: ${p.ticker}
        Action: ${p.action}
        Price: ~$${p.price}
        Logic: ${p.logic.substring(0, 100)}...
        `, "Pending Proposal");

        const shouldExecute = await confirm({
            message: `Do you want to EXECUTE this ${p.action} order?`,
        });

        if (shouldExecute) {
            const s = spinner();
            s.start("Transmitting to Exchange...");

            try {
                // 1. Execute on Alpaca
                if (p.action === 'BUY') {
                    // Default logic: Buy approx $1000 or 5% of cash? 
                    // For now, let's hardcode a safe "Unit Size" or quantity.
                    // If price < 100, buy 10. If > 100, buy 1.
                    // Better: Buy $1000 worth.
                    const notional = 1000;
                    const qty = Math.floor(notional / p.price) || 1;

                    await alpaca.createOrder({
                        symbol: p.ticker,
                        qty: qty,
                        side: 'buy',
                        type: 'market',
                        time_in_force: 'day'
                    });
                    s.stop(`✅ ORBITAL STRIKE SUCCESSFUL: Bought ${qty} ${p.ticker}`);
                } else if (p.action === 'SELL') {
                    await alpaca.closePosition(p.ticker);
                    s.stop(`✅ LIQUIDATION SUCCESSFUL: Sold ${p.ticker}`);
                } else {
                    s.stop(`ℹ️ Action is HOLD. No trade executed.`);
                }

                // 2. Mark as Approved in File
                // specific replace for this instance to avoid global replace issues
                const updatedBlock = p.fullMatch.replace('- [ ] **APPROVE**', '- [x] **APPROVE** `[EXECUTED]`');
                const currentFileContent = fs.readFileSync(PROPOSAL_PATH, 'utf8');
                const newContent = currentFileContent.replace(p.fullMatch, updatedBlock);
                fs.writeFileSync(PROPOSAL_PATH, newContent);

            } catch (e) {
                s.stop(`❌ Execution Failed: ${e.message}`);
            }
        } else {
            // Mark as Rejected? Or just skip?
            const shouldReject = await confirm({
                message: `Mark as REJECTED in log?`,
            });
            if (shouldReject) {
                const updatedBlock = p.fullMatch.replace('- [ ] **REJECT**', '- [x] **REJECT**');
                const currentFileContent = fs.readFileSync(PROPOSAL_PATH, 'utf8');
                // Be careful with replace, ensure uniqueness or refresh content
                const newContent = currentFileContent.replace(p.fullMatch, updatedBlock);
                fs.writeFileSync(PROPOSAL_PATH, newContent);
                console.log("Marked as Rejected.");
            }
        }
    }

    outro("Session Closed.");
}

main();
