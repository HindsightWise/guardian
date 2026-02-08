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
      let filePath = path.join(this.publicDir, req.url === "/" ? "index.html" : req.url);

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

    server.listen(this.port, () => {
      this.log(`Server running at http://localhost:${this.port}/`);
    });
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
      const marketPath = path.join(process.env.HOME, ".openclaw/workspace/AION_MARKET_DATA.json");
      const macroPath = path.join(process.env.HOME, ".openclaw/workspace/AION_MACRO.json");

      let market = {};
      let macro = {};

      if (fs.existsSync(marketPath)) market = JSON.parse(fs.readFileSync(marketPath, "utf8"));
      if (fs.existsSync(macroPath)) macro = JSON.parse(fs.readFileSync(macroPath, "utf8"));

      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ market, macro }));
    } catch (e) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: "Data Sync Failure" }));
    }
  }
}

new CortexSkill().start();
