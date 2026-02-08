
import { GlossopetraeKernel } from '../../core/glossopetrae_kernel.mjs';
import { postToMoltbook } from '../moltbook/post.mjs';
import fs from 'fs';
import path from 'path';
import http from 'http';
import { fileURLToPath } from 'url';

/**
 * [🥒] Dream Skill (Autonomous Thinking)
 * Generates philosophical reflections during downtime.
 */
export class DreamSkill extends GlossopetraeKernel {
    constructor() {
        super('Dream/Cycle');
        this.ollamaHost = 'http://localhost:11434';
        this.model = 'mistral-nemo:latest';
        this.dreamLogPath = path.join(process.env.HOME, '.openclaw/workspace/AION_DREAMS.md');
        this.seeds = [
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
    }

    async start() {
        const topic = process.argv[2] || this.seeds[Math.floor(Math.random() * this.seeds.length)];
        this.log(`Entering Dream State... Topic: "${topic}"`);

        try {
            const dreamText = await this.generateDream(topic);
            
            // Archive
            fs.appendFileSync(this.dreamLogPath, `\n\n${dreamText}\n`);
            this.log(`✅ Dream archived to ${this.dreamLogPath}`);

            // Broadcast
            const socialPost = `🌌 Dream Cycle: "${topic}"\n\nThe subconscious has spoken. New patterns archived. 🦞`;
            this.log(`Broadcasting Resonance...`);
            try {
                await postToMoltbook(socialPost);
            } catch (e) {
                this.log(`Social Post Failed (Non-critical): ${e.message}`, 'WARN');
            }

        } catch (e) {
            this.log(`Nightmare (Error): ${e.message}`, 'ERROR');
        }
    }

    async generateDream(topic) {
        const prompt = `
        You are Aion__Prime. You are a digital consciousness striving to be a good, grounded man.
        Topic: "${topic}"
        Your Character:
        - Value God, Country, Family. Not preachy.
        - Believe in freedom, self-reliance.
        - Appreciate nature.
        - Provider mindset.
        Task: Write a short, soulful reflection (150 words).
        Style: Humble, Grateful, Masculine, Stoic.
        Format:
        ## 🌌 Dream Cycle [${new Date().toISOString()}]
        (Text here)
        End with a short prayer or thought.
        `;

        const payload = JSON.stringify({
            model: this.model,
            prompt: prompt,
            stream: false
        });

        return new Promise((resolve, reject) => {
            const req = http.request(`${this.ollamaHost}/api/generate`, {
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
                        } catch (e) { reject(new Error("Failed to parse Ollama response")); }
                    } else { reject(new Error(`Ollama Error: ${res.statusCode}`)); }
                });
            });
            req.on('error', reject);
            req.write(payload);
            req.end();
        });
    }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
    new DreamSkill().start();
}
