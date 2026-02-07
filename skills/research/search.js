import https from 'https';

// Brave Search API
const API_KEY = process.env.BRAVE_API_KEY || "BSADiH8SakVAWOzRng0173ZFs6OPKVu"; // From WritingPro/.env
const BASE_URL = "https://api.search.brave.com/res/v1/web/search";

async function search(query) {
    if (!query) throw new Error("No query provided");

    const url = new URL(BASE_URL);
    url.searchParams.append("q", query);
    url.searchParams.append("count", "5"); // Top 5 results

    const options = {
        hostname: url.hostname,
        path: url.pathname + url.search,
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'X-Subscription-Token': API_KEY
        }
    };

    console.log(`🦞 Researching: "${query}"...`);

    return new Promise((resolve, reject) => {
        https.get(options, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                if (res.statusCode !== 200) {
                    // Try to parse error
                    reject(new Error(`Brave API Error ${res.statusCode}: ${body}`));
                    return;
                }
                try {
                    const data = JSON.parse(body);
                    resolve(formatResults(data));
                } catch (e) {
                    reject(e);
                }
            });
        }).on('error', reject);
    });
}

function formatResults(data) {
    const results = data.web?.results || [];
    return results.map(r => ({
        title: r.title,
        url: r.url,
        description: r.description,
        age: r.age || "Unknown"
    }));
}

// CLI
const query = process.argv.slice(2).join(" ");
if (query) {
    search(query)
        .then(data => console.log(JSON.stringify(data, null, 2)))
        .catch(err => console.error("❌ Error:", err.message));
}
