
import { GlossopetraeKernel } from '../../core/glossopetrae_kernel.mjs';
import { TwitterApi } from 'twitter-api-v2';
import dotenv from 'dotenv';
import path from 'path';

// Helper to load env since we are ESM
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

class TwitterSkill extends GlossopetraeKernel {
    constructor() {
        super('Twitter');
    }

    async postTweet(content) {
        this.log(`Attempting to tweet: "${content}"`);

        try {
            await this.loadConfig();

            const client = new TwitterApi({
                appKey: process.env.OPENCLAW_X_CONSUMER_KEY || this.config.apiKey,
                appSecret: process.env.OPENCLAW_X_CONSUMER_SECRET || this.config.apiSecret,
                accessToken: process.env.OPENCLAW_X_ACCESS_TOKEN || this.config.accessToken,
                accessSecret: process.env.OPENCLAW_X_ACCESS_TOKEN_SECRET || this.config.accessSecret,
            });

            const rwClient = client.readWrite;
            const result = await rwClient.v2.tweet(content);
            this.log(`Tweet posted! ID: ${result.data.id} - ${result.data.text}`);
        } catch (e) {
            this.log(`Tweet failed: ${e.message}`, 'ERROR');
            if (e.data) this.log(JSON.stringify(e.data, null, 2), 'ERROR');
        }
    }
}

const content = process.argv[2];
if (!content) {
    console.error("Usage: node tweet.mjs <content>");
    process.exit(1);
}

new TwitterSkill().postTweet(content);
