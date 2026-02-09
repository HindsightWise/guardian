#!/usr/bin/env node

/**
 * Antigravity Bridge for Pickle Rick
 *
 * Allows Antigravity to invoke Pickle Rick skills and tools programmatically.
 *
 * Usage:
 *   node scripts/antigravity_pickle.mjs [command] [args...]
 *
 * Commands:
 *   prd <description>      - Drafts a PRD using pr_factory.py
 *   init <task>            - Initializes a session
 *   help                   - Shows help
 */

import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, "..");
const TOOLS_DIR = path.join(PROJECT_ROOT, "tools", "pickle-rick");
const SCRIPTS_DIR = path.join(TOOLS_DIR, "scripts");

// Ensure we use the specialized python environment if needed, or system python
const PYTHON = "python3";

async function runScript(scriptName, args = []) {
  const scriptPath = path.join(SCRIPTS_DIR, scriptName);
  console.log(`Executing: ${PYTHON} ${scriptPath} ${args.join(" ")}`);

  return new Promise((resolve, reject) => {
    const proc = spawn(PYTHON, [scriptPath, ...args], {
      cwd: PROJECT_ROOT,
      stdio: "inherit",
      env: {
        ...process.env,
        PYTHONPATH: TOOLS_DIR, // Ensure imports work
      },
    });

    proc.on("close", (code) => {
      if (code === 0) resolve();
      else reject(new Error(`Process exited with code ${code}`));
    });
  });
}

const args = process.argv.slice(2);
const command = args[0];
const commandArgs = args.slice(1);

async function main() {
  try {
    switch (command) {
      case "prd":
        // Usage: prd "Task Description"
        // Invokes pr_factory.py
        await runScript("pr_factory.py", commandArgs);
        break;

      case "spawn":
        // Usage: spawn "Task Description"
        await runScript("spawn_rick.py", commandArgs);
        break;

      case "help":
      default:
        console.log(`
Pickle Rick Bridge for Antigravity

Commands:
  prd "Description"    Draft a PRD for a task.
  spawn "Description"  Spawn a Rick instance for a task.
                `);
    }
  } catch (error) {
    console.error("Bridge Error:", error.message);
    process.exit(1);
  }
}

main();
