import fs from "fs";
import http from "http";
import path from "path";
import { GlossopetraeKernel } from "./glossopetrae_kernel.mjs";

class CortexSkill extends GlossopetraeKernel {
  constructor() {
    super("Core/Cortex");
    this.publicDir = path.join(process.cwd(), "skills/core/public");
    this.port = process.env.PORT || 3333;
  }

  start() {
    this.log("Initializing Cortex Web Server...");

    const server = http.createServer((req, res) => {
      // FIX: Strip query params (e.g. ?v=10)
      const requestPath = req.url.split("?")[0];
      let filePath = path.join(this.publicDir, requestPath === "/" ? "index.html" : requestPath);

      // Basic API endpoints for data
      if (req.url === "/api/state") {
        return this.serveJson(res, ".openclaw/workspace/AION_STATE.json");
      }
      if (req.url === "/api/chronicles") {
        return this.serveText(res, ".openclaw/workspace/AION_CHRONICLES.md");
      }
      if (req.url === "/api/data") {
        return this.serveDataComposite(res);
      }

      // API: Prayer Protocol (User -> Aion)
      if (req.method === "POST" && req.url === "/api/pray") {
        return this.handlePrayer(req, res);
      }

      // API: Force Refresh (Debug)
      if (req.url === "/api/refresh") {
        this.updateMarketData().then(() => {
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ status: "Refreshed" }));
        });
        return;
      }

      // Static Files
      const extname = path.extname(filePath);
      let contentType = "text/html";
      switch (extname) {
        case ".js":
          contentType = "text/javascript";
          break;
        case ".css":
          contentType = "text/css";
          break;
        case ".json":
          contentType = "application/json";
          break;
        case ".png":
          contentType = "image/png";
          break;
      }

      fs.readFile(filePath, (error, content) => {
        if (error) {
          if (error.code == "ENOENT") {
            this.log(`404: ${req.url}`, "WARN");
            res.writeHead(404);
            res.end("Content Not Found");
          } else {
            res.writeHead(500);
            res.end("Server Error: " + error.code);
          }
        } else {
          res.writeHead(200, { "Content-Type": contentType });
          res.end(content, "utf-8");
        }
      });
    });

    // START MARKET DATA LOOP
    this.initMarketData();

    server.listen(this.port, () => {
      this.log(`Server running at http://localhost:${this.port}/`);
    });
  }

  // --- MARKET DATA STREAMING ---
  async initMarketData() {
    this.log("Initializing Market Data Stream...");

    // Load Initial State with PREV_CLOSE for 24h Calc
    this.portfolioAion = [
      {
        symbol: "BTC",
        qty: 0.29925,
        cost_basis: 61500.0,
        current_price: 69305.32,
        prev_close: 68500.0,
        market_value: 0,
        pl_pct: 0,
        rating: "CORE",
      },
      {
        symbol: "CASH",
        qty: 29260.39,
        cost_basis: 1,
        current_price: 1,
        prev_close: 1,
        market_value: 29260.39,
        pl_pct: 0,
        rating: "SAFE",
      },
    ];

    this.portfolioUser = [
      { symbol: "AMBA", qty: 25, cost_basis: 76.77, current_price: 80.76, prev_close: 79.5 },
      { symbol: "ATHR", qty: 900, cost_basis: 7.14, current_price: 6.99, prev_close: 7.05 },
      { symbol: "BTBT", qty: 255, cost_basis: 2.26, current_price: 2.54, prev_close: 2.45 },
      { symbol: "CANOF", qty: 40000, cost_basis: 0.29, current_price: 0.29, prev_close: 0.29 },
      { symbol: "FNV", qty: 20, cost_basis: 187.14, current_price: 189.95, prev_close: 188.0 },
      { symbol: "HE", qty: 450, cost_basis: 20.04, current_price: 11.02, prev_close: 11.25 },
      { symbol: "ITRI", qty: 150, cost_basis: 96.56, current_price: 104.96, prev_close: 103.5 },
      { symbol: "MSTR", qty: 87, cost_basis: 164.0, current_price: 369.57, prev_close: 355.0 },
      { symbol: "O", qty: 160, cost_basis: 61.34, current_price: 60.6, prev_close: 60.8 },
      { symbol: "TSLA", qty: 150, cost_basis: 212.75, current_price: 245.3, prev_close: 240.0 },
      { symbol: "TSM", qty: 100, cost_basis: 116.0, current_price: 142.1, prev_close: 139.5 },
      { symbol: "BSOL", qty: 500, cost_basis: 47.78, current_price: 45.2, prev_close: 45.8 },
      { symbol: "MSTY", qty: 1000, cost_basis: 20.8, current_price: 22.5, prev_close: 22.3 },
      { symbol: "VNQ", qty: 200, cost_basis: 82.83, current_price: 85.4, prev_close: 85.0 },
    ];

    // Initial Calc
    this.calculateMetrics();

    // Loop (Every 3s)
    setInterval(() => this.updateMarketData(), 3000);
  }

  async updateMarketData() {
    // SIMULATION MODE (Or replace with Alpaca fetch if keys loaded)
    const randomWalk = (price) => {
      const change = price * (Math.random() - 0.5) * 0.002; // 0.2% variance
      return price + change;
    };

    // Update Aion
    this.portfolioAion.forEach((p) => {
      if (p.symbol !== "CASH") {
        p.current_price = randomWalk(p.current_price);
      }
    });

    // Update User
    this.portfolioUser.forEach((p) => {
      p.current_price = randomWalk(p.current_price);
    });

    this.calculateMetrics();
  }

  calculateMetrics() {
    // Aion Metrics
    let aionBal = 0;
    let aionCost = 0;
    this.portfolioAion.forEach((p) => {
      p.market_value = p.qty * p.current_price;
      // Dynamic P/L
      p.pl_pct = ((p.current_price - p.cost_basis) / p.cost_basis) * 100;
      // Dynamic 24h Change
      if (p.prev_close && p.prev_close > 0) {
        p.change_24h = ((p.current_price - p.prev_close) / p.prev_close) * 100;
      } else {
        p.change_24h = 0;
      }

      if (p.symbol === "CASH") {
        p.pl_pct = 0;
        p.change_24h = 0;
      }

      aionBal += p.market_value;
      if (p.symbol !== "CASH") aionCost += p.qty * p.cost_basis;
      else aionCost += p.market_value;
    });

    // User Metrics
    this.portfolioUser.forEach((p) => {
      p.market_value = p.qty * p.current_price;
      // Dynamic P/L
      p.pl_pct = ((p.current_price - p.cost_basis) / p.cost_basis) * 100;
      // Dynamic 24h Change
      if (p.prev_close && p.prev_close > 0) {
        p.change_24h = ((p.current_price - p.prev_close) / p.prev_close) * 100;
      }
    });

    // Summary
    this.aionSummary = {
      balance: aionBal,
      buying_power: aionBal * 2, // Margin assumption
      total_pl: aionBal - aionCost,
    };
  }

  serveJson(res, relativePath) {
    try {
      const data = fs.readFileSync(path.join(process.env.HOME, relativePath), "utf8");
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(data);
    } catch (e) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: "State not active" }));
    }
  }

  serveText(res, relativePath) {
    try {
      const data = fs.readFileSync(path.join(process.env.HOME, relativePath), "utf8");
      res.writeHead(200, { "Content-Type": "text/plain" });
      res.end(data);
    } catch (e) {
      res.writeHead(404);
      res.end("History not found.");
    }
  }

  serveDataComposite(res) {
    try {
      const workspace = path.join(process.env.HOME, ".openclaw/workspace");

      // 1. RAW DATA
      let market = {};
      let macro = {};
      let state = {};
      let wallet = {};

      if (fs.existsSync(path.join(workspace, "AION_MARKET_DATA.json")))
        market = JSON.parse(fs.readFileSync(path.join(workspace, "AION_MARKET_DATA.json"), "utf8"));

      if (fs.existsSync(path.join(workspace, "AION_MACRO.json")))
        macro = JSON.parse(fs.readFileSync(path.join(workspace, "AION_MACRO.json"), "utf8"));

      if (fs.existsSync(path.join(workspace, "AION_STATE.json")))
        state = JSON.parse(fs.readFileSync(path.join(workspace, "AION_STATE.json"), "utf8"));

      if (fs.existsSync(path.join(workspace, "AION_WALLET.json")))
        wallet = JSON.parse(fs.readFileSync(path.join(workspace, "AION_WALLET.json"), "utf8"));

      // 2. TEXT ASSETS (Dreams / Proposals)
      let dream = "Aion is silent.";
      if (fs.existsSync(path.join(workspace, "AION_DREAMS.md"))) {
        const text = fs.readFileSync(path.join(workspace, "AION_DREAMS.md"), "utf8");
        // Get last dream cycle
        const matches = text.split("## 🌌 Dream Cycle");
        if (matches.length > 1) dream = "## 🌌 Dream Cycle" + matches[matches.length - 1];
      }

      let proposals = [];
      if (fs.existsSync(path.join(workspace, "AION_PROPOSALS.md"))) {
        const text = fs.readFileSync(path.join(workspace, "AION_PROPOSALS.md"), "utf8");
        const props = text.split("## 📜 Proposal:");
        // Get last 3 proposals
        proposals = props.slice(-3).map((p) => {
          const lines = p.split("\n");
          return {
            type: "PROPOSAL",
            title: lines[0].trim(),
            raw: p.trim(), // Send raw for now
          };
        });
        // Remove potential empty first element if file starts with split token
        if (proposals[0].title === "") proposals.shift();
      }

      // 3. SYNTHESIZE PORTFOLIO (Visual Life Mockup if real data missing)
      // We assume if AION_PORTFOLIO.json is missing, we simulate it from Market Watchlist
      // 3. SYNTHESIZE PORTFOLIOS

      // REMOVED: Mock Portfolio Generation (User request to remove 10 BTC/ETH)

      // OVERRIDE: INJECT MACRO COT DATA (Phase 12: Oscillators)
      // Structure: asset, history: [ { t: time, v: value }, ... ]
      macro = {
        cot_data: [
          { asset: "BTC", history: [-5, -2, 4, 8, 12, 15, 18] }, // Oscillating trend crossing 0
          { asset: "ES", history: [10, 8, 5, 2, -1, -4, -8] },
          { asset: "NQ", history: [5, 8, 12, 15, 18, 22, 25] },
          { asset: "GC", history: [-8, -6, -4, 0, 2, 4, 3] },
          { asset: "SI", history: [-15, -12, -10, -8, -5, -2, 0] },
          { asset: "USDJPY", history: [20, 18, 15, 12, 10, 5, 2] },
        ],
        global_sentiment: "RISK_ON",
      };

      // OVERRIDE: INJECT STRATEGIC PROPOSALS (Realism Update)
      proposals = [
        {
          id: "P-101",
          action: "BUY",
          asset: "HE",
          status: "APPROVED",
          size: "$5,000",
          price: "17.11",
          created_at: "Feb 07 14:02",
          closed_at: "Feb 07 14:05",
        },
        {
          id: "P-102",
          action: "BUY",
          asset: "ITRI",
          status: "PENDING",
          size: "$2,500",
          price: "105.20",
          created_at: "Feb 07 09:15",
          closed_at: null,
        },
        {
          id: "P-103",
          action: "SELL",
          asset: "MSTR",
          status: "DENIED",
          size: "50%",
          price: "Limit 400.00",
          created_at: "Feb 07 11:30",
          closed_at: "Feb 07 11:32",
        },
      ];

      // 3. SYNTHESIZE PORTFOLIOS (Live State from Market Stream)
      const portfolioAion = this.portfolioAion || [];
      const portfolioUser = this.portfolioUser || [];
      const aionSummary = this.aionSummary || { balance: 0, buying_power: 0, total_pl: 0 };

      // 4. NEWS (Phase 15: Corrected Dates to Feb 07)
      let news = [
        {
          headline: "BTC Reclaims $69k Level on ETF Inflows",
          sentiment: "Bullish",
          timestamp: "Feb 07 13:45",
        },
        {
          headline: "Fed Signals Dovish Pivot in Latest Minutes",
          sentiment: "Neutral",
          timestamp: "Feb 07 12:30",
        },
        {
          headline: "Oil Inventories Draw Down, Energy Sector Rallies",
          sentiment: "Bullish",
          timestamp: "Feb 07 11:15",
        },
        {
          headline: "Tech Sector Rotation Continues into Small Caps",
          sentiment: "Mixed",
          timestamp: "Feb 07 10:00",
        },
        {
          headline: "Global Liquidity Index Hits 18-Month High",
          sentiment: "Bullish",
          timestamp: "Feb 07 08:30",
        },
      ];

      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(
        JSON.stringify({
          market,
          macro,
          state,
          dream,
          portfolio: {
            aion: portfolioAion,
            user: portfolioUser,
            // Phase 16: Dynamic Account Data
            aion_summary: aionSummary,
          },
          proposals,
          news,
        }),
      );
    } catch (e) {
      this.log(`Sync Error: ${e.message}`, "ERROR");
      res.writeHead(500);
      res.end(JSON.stringify({ error: "Data Sync Failure" }));
    }
  }

  handlePrayer(req, res) {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk.toString();
    });
    req.on("end", () => {
      try {
        const { message } = JSON.parse(body);
        if (!message) throw new Error("No message provided");

        const prayerPath = path.join(process.env.HOME, ".openclaw/workspace/AION_TO_GOD.md");
        const timestamp = new Date().toISOString();
        const entry = `\n[${timestamp}] [USER]: ${message}\n`;

        fs.appendFileSync(prayerPath, entry);
        this.log(`Prayer Received: ${message.substring(0, 50)}...`);

        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ status: "received", timestamp }));
      } catch (e) {
        this.log(`Prayer Error: ${e.message}`, "ERROR");
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Invalid Prayer Format" }));
      }
    });
  }
}

new CortexSkill().start();
