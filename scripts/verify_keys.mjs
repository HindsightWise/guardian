import "dotenv/config";
import axios from "axios";
import { TwitterApi } from "twitter-api-v2";

// Load env
const env = process.env;

const results = {};

async function testTwitter() {
  try {
    const client = new TwitterApi({
      appKey: env.OPENCLAW_X_CONSUMER_KEY,
      appSecret: env.OPENCLAW_X_CONSUMER_SECRET,
      accessToken: env.OPENCLAW_X_ACCESS_TOKEN,
      accessSecret: env.OPENCLAW_X_ACCESS_TOKEN_SECRET,
    });
    const me = await client.v2.me();
    results.Twitter = `OK (User: ${me.data.username})`;
  } catch (e) {
    results.Twitter = `FAIL (${e.message})`;
  }
}

async function testTavily() {
  try {
    const res = await axios.post("https://api.tavily.com/search", {
      api_key: env.TAVILY_API_KEY,
      query: "test",
      search_depth: "basic",
    });
    results.Tavily = res.status === 200 ? "OK" : "FAIL";
  } catch (e) {
    results.Tavily = `FAIL (${e.message})`;
  }
}

async function testAlpaca() {
  try {
    const res = await axios.get(`${env.ALPACA_API_ENDPOINT}/account`, {
      headers: {
        "APCA-API-KEY-ID": env.ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": env.ALPACA_SECRET_KEY,
      },
    });
    results.Alpaca = res.status === 200 ? `OK (Cash: ${res.data.cash})` : "FAIL";
  } catch (e) {
    results.Alpaca = `FAIL (${e.message})`;
  }
}

async function testFMP() {
  try {
    // Use stable endpoint as verified by user
    const res = await axios.get(
      `https://financialmodelingprep.com/stable/income-statement?symbol=AAPL&apikey=${env.FMP_API_KEY}`,
    );
    results.FMP = res.status === 200 && res.data ? "OK" : "FAIL";
  } catch (e) {
    results.FMP = `FAIL (${e.message})`;
  }
}

async function testOpenWeather() {
  try {
    const res = await axios.get(
      `https://api.openweathermap.org/data/2.5/weather?q=London&appid=${env.OPENWEATHERMAP_API_KEY}`,
    );
    results.OpenWeather = res.status === 200 ? "OK" : "FAIL";
  } catch (e) {
    results.OpenWeather = `FAIL (${e.message})`;
  }
}

async function main() {
  console.log("Testing API Keys...");
  await Promise.all([testTwitter(), testTavily(), testAlpaca(), testFMP(), testOpenWeather()]);
  console.table(results);
}

main();
