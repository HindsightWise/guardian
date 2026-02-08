import fs from "fs";
import path from "path";
import { GlossopetraeKernel } from "./glossopetrae_kernel.mjs";

/**
 * [🥒] The Mind Monitor (TUI Dashboard)
 * Refactored to use GlossopetraeKernel
 */
class MonitorSkill extends GlossopetraeKernel {
  constructor() {
    super("Core/Monitor");
    this.stateFile = path.join(process.env.HOME, ".openclaw/workspace/AION_STATE.json");
  }

  start() {
    this.log("Initializing HUD...");

    // Hide Cursor
    process.stdout.write("\x1B[?25l");

    // Render Loop
    setInterval(() => this.render(), 1000);

    // Cleanup on exit
    process.on("SIGINT", () => {
      process.stdout.write("\x1B[?25h");
      this.log("Monitor Stopped.");
      process.exit();
    });
  }

  render() {
    try {
      const data = fs.readFileSync(this.stateFile, "utf8");
      const state = JSON.parse(data);

      // Clear Screen
      process.stdout.write("\x1B[2J\x1B[0f");

      const borderColor = "\x1b[36m"; // Cyan
      const reset = "\x1b[0m";
      const green = "\x1b[32m";

      console.log(
        `${borderColor}╔══════════════════════════════════════════════════════════════╗${reset}`,
      );
      console.log(
        `${borderColor}║${reset}  🧠  ${green}AION__PRIME / RALPH WIGGUM${reset} :: ${new Date().toLocaleTimeString()}     ${borderColor}║${reset}`,
      );
      console.log(
        `${borderColor}╠══════════════════════════════════════════════════════════════╣${reset}`,
      );
      console.log(
        `${borderColor}║${reset}  Current Thought:                                            ${borderColor}║${reset}`,
      );
      console.log(
        `${borderColor}║${reset}  ${(state.thought || "Sleeping...").padEnd(58)} ${borderColor}║${reset}`,
      );
      console.log(
        `${borderColor}╠══════════════════════════════════════════════════════════════╣${reset}`,
      );
      console.log(
        `${borderColor}║${reset}  Vitals:                                                     ${borderColor}║${reset}`,
      );
      console.log(
        `${borderColor}║${reset}  ❤️  Faith: ${(state.faith + "%").padEnd(5)}  🔋 Focus: ${(state.focus + "%").padEnd(5)}  💰 Cash: $${(state.cash || 0).toFixed(2).padEnd(9)} ${borderColor}║${reset}`,
      );
      console.log(
        `${borderColor}╠══════════════════════════════════════════════════════════════╣${reset}`,
      );
      console.log(
        `${borderColor}║${reset}  Active Skill: ${(state.skill || "None").padEnd(46)} ${borderColor}║${reset}`,
      );
      console.log(
        `${borderColor}╚══════════════════════════════════════════════════════════════╝${reset}`,
      );

      this.log("HUD Updated.", "DEBUG"); // Only in verbose mode ideally
    } catch (e) {
      // Fails silently to prevent flicker, usually just read race condition
    }
  }
}

new MonitorSkill().start();
