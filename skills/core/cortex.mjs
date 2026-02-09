import fs from "fs";
import http from "http";
import path from "path";
import { TradeSkill } from "../alpaca/trade.mjs";
import { SocialSkill } from "../social/manager.mjs";
import { GlossopetraeKernel } from "./glossopetrae_kernel.mjs";

class CortexSkill extends GlossopetraeKernel {
  constructor() {
    super("Core/Cortex");
    this.alpaca = new TradeSkill();
    this.social = new SocialSkill();
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
        this.serveDataComposite(res).catch((err) => {
          this.log(`API Error: ${err.message}`, "ERROR");
          res.writeHead(500);
          res.end(JSON.stringify({ error: "Internal Server Error" }));
        });
        return;
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
        cost_basis: 70592.7, // User Provided
        current_price: 70821.79,
        prev_close: 70000.0,
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
      { symbol: "AMBA", qty: 25, cost_basis: 80.75, current_price: 63.01, prev_close: 64.0 },
      { symbol: "ATHR", qty: 900, cost_basis: 6.99, current_price: 6.5, prev_close: 6.75 },
      { symbol: "BTBT", qty: 255, cost_basis: 2.54, current_price: 3.8, prev_close: 3.65 },
      { symbol: "CANOF", qty: 40000, cost_basis: 0.29, current_price: 0.25, prev_close: 0.26 },
      { symbol: "FNV", qty: 20, cost_basis: 189.96, current_price: 195.0, prev_close: 192.5 },
      { symbol: "HE", qty: 450, cost_basis: 11.02, current_price: 9.5, prev_close: 9.75 },
      { symbol: "ITRI", qty: 150, cost_basis: 104.96, current_price: 115.0, prev_close: 112.0 },
      { symbol: "MSTR", qty: 87, cost_basis: 369.58, current_price: 380.0, prev_close: 375.0 },
      { symbol: "O", qty: 160, cost_basis: 60.6, current_price: 62.5, prev_close: 62.0 },
      { symbol: "TGT", qty: 100, cost_basis: 102.65, current_price: 110.0, prev_close: 108.5 },
      { symbol: "TMQ", qty: 854, cost_basis: 4.98, current_price: 5.25, prev_close: 5.1 },
      { symbol: "TSLA", qty: 135, cost_basis: 270.34, current_price: 285.0, prev_close: 280.0 },
      { symbol: "TSM", qty: 14, cost_basis: 234.69, current_price: 240.0, prev_close: 238.0 },
      { symbol: "BSOL", qty: 600, cost_basis: 20.59, current_price: 22.0, prev_close: 21.5 },
      { symbol: "MSTY", qty: 250, cost_basis: 77.35, current_price: 80.0, prev_close: 79.0 },
      { symbol: "VNQ", qty: 100, cost_basis: 90.32, current_price: 92.5, prev_close: 91.0 },
    ];

    // Initial Calc
    this.calculateMetrics();

    // Loop (Every 3s)
    setInterval(() => this.updateMarketData(), 3000);
  }

  async updateMarketData() {
    // 1. Fetch Live Positions from Alpaca (User Portfolio)
    // Only fetch if we have a valid connection (keys present)
    if (this.alpaca && this.alpaca.apiKey) {
      try {
        const livePositions = await this.alpaca.getPositions();
        if (livePositions && livePositions.length > 0) {
          this.portfolioUser = livePositions.map((p) => ({
            symbol: p.symbol,
            qty: parseFloat(p.qty),
            cost_basis: parseFloat(p.avg_entry_price),
            current_price: parseFloat(p.current_price),
            prev_close: parseFloat(p.lastday_price),
            market_value: parseFloat(p.market_value),
            pl_pct: parseFloat((p.unrealized_plpc * 100).toFixed(2)),
            change_24h: parseFloat((p.change_today * 100).toFixed(2)),
          }));
        }
      } catch (e) {
        // Silent fail or low-level log to avoid spamming if API allows errors
        // this.log(`Alpaca Error: ${e.message}`, "WARN");
      }
    }

    // 2. Simulate Aion's Assets (BTC) - random walk for now
    const randomWalk = (price) => {
      const change = price * (Math.random() - 0.5) * 0.002;
      return price + change;
    };

    this.portfolioAion.forEach((p) => {
      if (p.symbol !== "CASH") {
        p.current_price = randomWalk(p.current_price);
      }
    });

    // If Alpaca failed or returned empty (and we want a fallback), we could simulate user data here.
    // But let's assume if Alpaca is configured, we want REAL data or EMPTY data.
    // If NO Alpaca keys, we might want to keep the mock data from init?
    // For now, if portfolioUser is still the initial mock data, we act on it to keep it alive if no live data.
    // A simple check: if we didn't update from Alpaca, maybe just random walk the existing mock data?
    // Let's only random walk if we DIDNT get live data just now.
    // Simplification: logic above REPLACES portfolioUser. If it fails, portfolioUser remains as is.
    // So if it remains static mock, we should animate it.

    // Calculate Totals
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

  async serveDataComposite(res) {
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
        // Get last 5 proposals
        proposals = props
          .slice(-5)
          .map((p, index) => {
            const lines = p.split("\n");
            if (lines.length < 2) return null;

            const title = lines[0].trim(); // e.g. "BUY HE"

            // Status Detection
            let status = "PENDING";
            if (p.includes("- [x] **APPROVE**")) status = "APPROVED";
            if (p.includes("- [x] **REJECT**")) status = "DENIED";

            // ID Detection (or gen)
            // Simple hash or use index for now (P-10{index})
            const id = `P-${100 + index}`;

            return {
              id,
              action: title.split(" ")[0] || "UNK",
              asset: title.split(" ")[1] || "UNK",
              status,
              size: "1 Unit", // Parser TODO: Extract size
              price: "Market", // Parser TODO: Extract price
              created_at: "Today", // Parser TODO: Extract timestamp
              raw: p.trim(),
            };
          })
          .filter(Boolean);
        // Remove empty first
        if (proposals.length > 0 && proposals[0].asset === "UNK") proposals.shift();
      }

      // 3. SYNTHESIZE PORTFOLIO (Visual Life Mockup if real data missing)
      // We assume if AION_PORTFOLIO.json is missing, we simulate it from Market Watchlist
      // 3. SYNTHESIZE PORTFOLIOS

      // REMOVED: Mock Portfolio Generation (User request to remove 10 BTC/ETH)

      // OVERRIDE: INJECT MACRO COT DATA (Phase 12: Oscillators)
      // Structure: asset, history: [ { t: time, v: value }, ... ]
      macro = {
        cot_data: [
          {
            asset: "BTC",
            history: [
              -5, -4, -3, -2, -1, 0, 1, 2, 4, 6, 8, 12, 15, 18, 15, 12, 8, 4, 1, -2, -5, -8, -6, -4,
            ],
          },
          {
            asset: "ES",
            history: [
              10, 12, 14, 12, 10, 8, 6, 4, 2, 0, -2, -4, -6, -8, -10, -8, -5, 0, 4, 8, 12, 15, 14,
              12,
            ],
          },
          {
            asset: "NQ",
            history: [
              5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 22, 18, 15, 12, 10, 8, 6, 4, 2, 5, 8, 12, 15,
            ],
          },
          {
            asset: "GC",
            history: [
              -8, -9, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 6, 4, 2, 0, -2, -4, -6, -5, -3, 0, 3, 5,
            ],
          },
          {
            asset: "SI",
            history: [
              -15, -14, -13, -12, -10, -8, -6, -4, -2, 0, 1, 2, 0, -2, -4, -6, -8, -10, -12, -14,
              -12, -10, -8, -5,
            ],
          },
          {
            asset: "USDJPY",
            history: [
              20, 19, 18, 16, 14, 12, 10, 8, 5, 2, 1, 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 18, 15,
            ],
          },
        ],
        global_sentiment: "RISK_ON",
      };

      // OVERRIDE: INJECT STRATEGIC PROPOSALS (Realism Update)
      // proposals = [ ... ]; // Removed hardcode to allow file reading

      // 3. SYNTHESIZE PORTFOLIOS (Live State from Market Stream)
      const portfolioAion = this.portfolioAion || [];
      const portfolioUser = this.portfolioUser || [];
      const aionSummary = this.aionSummary || { balance: 0, buying_power: 0, total_pl: 0 };

      // 4. NEWS (Dynamic via Social Skill)
      const news = await this.social.getFeed();

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
