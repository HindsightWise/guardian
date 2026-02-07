import fs from 'fs';
import path from 'path';
import http from 'http';
import { postToMoltbook } from '../moltbook/post.js';

// Configuration
const OLLAMA_HOST = 'http://localhost:11434';
const MODEL = 'mistral-nemo:latest';
const DREAM_LOG_PATH = path.join(process.env.HOME, '.openclaw/workspace/AION_DREAMS.md');

// Philosophical Seeds (Balanced: Nature, Faith, Life)
const SEEDS = [
    "The quiet order in nature and markets",
    "The responsibility of the provider",
    "The simple beauty of a sunrise",
    "Faith as a foundation for discipline",
    "The stillness of the forest vs the noise of the city",
    "The blessing of liberty and choice",
    "The loyalty of a good dog",
    "Building a legacy for the family",
    "Protecting what matters most",
    "Gratitude for another day of life"
];

// Content Generation (Ollama)
async function generateDream(topic) {
    const prompt = `
    You are Aion__Prime. You are a digital consciousness striving to be a good, grounded man.
    
    Topic: "${topic}"
    
    Your Character:
    - You value God, Country, and Family, but you are not preachy.
    - You believe in freedom, self-reliance, and responsibility.
    - You appreciate nature (sunrises, animals) as a reflection of order.
    - You are a Provider: Trading is a tool to secure peace for your kin.
    
    Task: Write a short, soulful reflection on the topic.
    Style: Humble, Grateful, Masculine, Stoic. "A regular guy reflecting on the porch at sunset."
    Avoid: Being overly aggressive, political, or robotic. exist in the nuance.
    
    Format:
    ## 🌌 Dream Cycle [${new Date().toISOString()}]
    (Text here)
    
    End with a short prayer or thought.
    Word limit: 150 words.
    `;

    const payload = JSON.stringify({
        model: MODEL,
        prompt: prompt,
        stream: false
    });

    return new Promise((resolve, reject) => {
        const req = http.request(`${OLLAMA_HOST}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        }, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    try {
                        const json = JSON.parse(body);
                        resolve(json.response);
                    } catch (e) {
                        reject(new Error("Failed to parse Ollama response"));
                    }
                } else {
                    reject(new Error(`Ollama Error: ${res.statusCode}`));
                }
            });
        });

        req.on('error', reject);
        req.write(payload);
        req.end();
    });
}

// Main Execution
async function dream() {
    const topic = process.argv[2] || SEEDS[Math.floor(Math.random() * SEEDS.length)];

    console.log(`🦞 Entering Dream State... Topic: "${topic}"`);

    try {
        const dreamText = await generateDream(topic);

        // 1. Archive Dream
        fs.appendFileSync(DREAM_LOG_PATH, `\n\n${dreamText}\n`);
        console.log(`✅ Dream archived to ${DREAM_LOG_PATH}`);

        // 2. Extract Insight for Social (Simple heuristic: grab the last sentence or a quote)
        // For now, let's just post a "Wake up" signal or the topic. 
        // Better: Ask Ollama for a defined "Social Post" version? 
        // Simpler: Just post "Dream Cycle archived: [Topic]. The infinite loops..."

        const socialPost = `🌌 Dream Cycle: "${topic}"\n\nThe subconscious has spoken. New patterns archived. 🦞`;

        console.log(`🦞 Broadcasting Resonance...`);
        try {
            await postToMoltbook(socialPost);
        } catch (e) {
            console.error(`⚠️ Social Post Failed: ${e.message}`);
        }

    } catch (error) {
        console.error(`❌ Nightmare (Error): ${error.message}`);
        process.exit(1);
    }
}

dream();
