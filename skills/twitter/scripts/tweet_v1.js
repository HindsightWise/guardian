const { TwitterApi } = require('twitter-api-v2');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

const client = new TwitterApi({
    appKey: process.env.OPENCLAW_X_CONSUMER_KEY,
    appSecret: process.env.OPENCLAW_X_CONSUMER_SECRET,
    accessToken: process.env.OPENCLAW_X_ACCESS_TOKEN,
    accessSecret: process.env.OPENCLAW_X_ACCESS_TOKEN_SECRET,
});

async function tweetV1() {
    const text = process.argv[2];
    if (!text) {
        console.error('Usage: node tweet_v1.js "Your tweet text"');
        process.exit(1);
    }
    try {
        // Attempt v1.1 post
        const createdTweet = await client.v1.tweet(text);
        console.log(JSON.stringify(createdTweet, null, 2));
    } catch (e) {
        console.error('Error posting tweet (v1):', e);
        if (e.data) console.error(JSON.stringify(e.data, null, 2));
        process.exit(1);
    }
}

tweetV1();
