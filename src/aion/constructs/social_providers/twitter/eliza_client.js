const { Scraper } = require('agent-twitter-client');
const fs = require('fs');
const path = require('path');

async function postTweet(text) {
    const scraper = new Scraper();
    
    const cookiePath = path.join(process.cwd(), 'twitter_cookies.json');
    if (!fs.existsSync(cookiePath)) {
        console.error("❌ twitter_cookies.json missing.");
        process.exit(1);
    }

    const state = JSON.parse(fs.readFileSync(cookiePath, 'utf8'));
    
    // Normalize cookies for twitter.com
    const cookies = state.cookies.map(c => {
        // Force x.com cookies to twitter.com so tough-cookie doesn't complain
        const domain = c.domain.replace('x.com', 'twitter.com');
        return `${c.name}=${c.value}; Domain=${domain}; Path=${c.path}; ${c.secure ? 'Secure' : ''}; ${c.httpOnly ? 'HttpOnly' : ''}`;
    });
    
    console.log("Setting cookies...");
    try {
        await scraper.setCookies(cookies);
    } catch (e) {
        console.warn("⚠️ Cookie warning:", e.message);
    }

    console.log("Checking login status...");
    const loggedIn = await scraper.isLoggedIn();
    if (loggedIn) {
        console.log("✅ Session verified.");
        await scraper.sendTweet(text);
        console.log("✅ Tweet sent via ElizaOS protocol.");
    } else {
        console.error("❌ Cookie session rejected by X. Trying fallback login...");
        try {
            await scraper.login("Aion__Prime", "jiqwox-gotraz-ratVe1", "zerbytheboss@gmail.com");
            if (await scraper.isLoggedIn()) {
                console.log("✅ Re-authenticated successfully.");
                await scraper.sendTweet(text);
                console.log("✅ Tweet sent.");
            } else {
                console.error("❌ Full authentication failure.");
                process.exit(1);
            }
        } catch (e) {
            console.error("❌ Login Error:", e.message);
            process.exit(1);
        }
    }
}

const args = process.argv.slice(2);
if (args.length > 0) {
    postTweet(args[0]).catch(err => {
        console.error(err);
        process.exit(1);
    });
}
