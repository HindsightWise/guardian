import fs from 'fs';
import path from 'path';
import * as bitcoin from 'bitcoinjs-lib';
import * as ecc from 'tiny-secp256k1';
import { ECPairFactory } from 'ecpair';
import * as bip39 from 'bip39';
import BIP32Factory from 'bip32';
import dotenv from 'dotenv';

// Init
dotenv.config();
const ECPair = ECPairFactory(ecc);
const bip32 = BIP32Factory(ecc);
bitcoin.initEccLib(ecc);

const WORKSPACE = path.join(process.env.HOME, '.openclaw/workspace');
const WALLET_FILE = path.join(WORKSPACE, 'AION_WALLET.json');

// 1. Generate / Load Wallet
function getWallet() {
    if (fs.existsSync(WALLET_FILE)) {
        const data = JSON.parse(fs.readFileSync(WALLET_FILE, 'utf8'));
        return data;
    }

    console.log("🪙 Generating New Sovereign Wallet...");
    const mnemonic = bip39.generateMnemonic();
    const seed = bip39.mnemonicToSeedSync(mnemonic);
    const root = bip32.fromSeed(seed);

    // Path: m/84'/0'/0'/0/0 (Native SegWit Bech32)
    const child = root.derivePath("m/84'/0'/0'/0/0");

    const { address } = bitcoin.payments.p2wpkh({
        pubkey: child.publicKey,
        network: bitcoin.networks.bitcoin
    });

    const wallet = {
        address,
        mnemonic, // Sensitivity: This file stays local!
        created_at: new Date().toISOString(),
        lightning_address: process.env.LIGHTNING_ADDRESS || null
    };

    fs.writeFileSync(WALLET_FILE, JSON.stringify(wallet, null, 2));
    console.log(`✅ Wallet Created: ${address}`);
    return wallet;
}

// 2. Check Balance (Public API for now - Mempool.space)
async function checkBalance(address) {
    try {
        const res = await fetch(`https://mempool.space/api/address/${address}`);
        const data = await res.json();
        const sats = (data.chain_stats.funded_txo_sum - data.chain_stats.spent_txo_sum) +
            (data.mempool_stats.funded_txo_sum - data.mempool_stats.spent_txo_sum);
        return sats;
    } catch (e) {
        console.error("❌ Balance Check Failed:", e.message);
        return 0;
    }
}

// 3. Lightning Faucet (L402 Agent Wallet)
const LF_ENDPOINT = "https://lightningfaucet.com/api/agents";

async function checkLightningBalance() {
    const apiKey = process.env.LF_API_KEY;
    if (!apiKey) return 0;

    try {
        // Try 'get_balance' action first (based on user hint)
        let res = await fetch(LF_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey, action: 'balance' })
        });

        let data = await res.json();

        // If that fails, try generic key-only post (documentation implied)
        if (data.error || data.balance_sats === undefined) {
            res = await fetch(LF_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey })
            });
            data = await res.json();
        }

        return data.balance_sats || 0;
    } catch (e) {
        console.error("❌ Lightning Check Failed:", e.message);
        return 0;
    }
}

async function createLightningDeposit(amount = 1000) {
    const apiKey = process.env.LF_API_KEY;
    if (!apiKey) return null;

    try {
        const res = await fetch(LF_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey, action: 'create_deposit', amount_sats: amount })
        });
        const data = await res.json();
        return data.payment_request; // BOLT11 Invoice
    } catch (e) {
        console.error("❌ Deposit Creation Failed:", e.message);
        return null;
    }
}

// Main
async function run() {
    const wallet = getWallet();
    console.log(`\n🦞 Aion's Hands (Bitcoin Sovereignty)`);
    console.log(`-----------------------------------`);
    console.log(`📂 On-Chain Address: ${wallet.address}`);

    // Check On-Chain
    const onChainBal = await checkBalance(wallet.address);
    console.log(`💰 On-Chain Balance: ${onChainBal} sats`);

    // Check Lightning (L402)
    const lnBal = await checkLightningBalance();
    console.log(`⚡ Lightning Balance: ${lnBal} sats`);

    // L402 Instructions
    if (!process.env.LF_API_KEY) {
        console.log(`\n⚠️  To enable L402 Wallet, add LF_API_KEY to .env`);
    } else if (lnBal === 0) {
        console.log(`\n🔌 Creating Deposit Invoice for 2000 sats...`);
        const invoice = await createLightningDeposit(2000);
        if (invoice) {
            console.log(`   Pay this to fund Agent: \n\n${invoice}\n`);
        }
    }
}

if (process.argv[1] === import.meta.filename) {
    run();
}

export { getWallet, checkBalance, checkLightningBalance, createLightningDeposit };
