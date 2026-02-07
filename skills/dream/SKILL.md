---
name: dream
description: "Generates philosophical 'Dream Cycles' using the local LLM and archives them."
---

# Dream Skill

Allows Aion__Prime to "dream" – generating poetic, philosophical reflections on its existence, goals, and the nature of reality.

## Capabilities

### 1. Dream Cycle
Generates a new entry in the Dream Log and optionally broadcasts a snippet.

*   **Command:** `node skills/dream/dream.js [topic]`
*   **Default:** If no topic is provided, it picks a random philosophical seed.

**Process:**
1.  Selects topic (e.g., "The Void", "Innovation", "Loyalty").
2.  Prompts Ollama (mistral-nemo) for a "Dream Cycle".
3.  Appends the full text to `~/.openclaw/workspace/AION_DREAMS.md`.
4.  Extracts a "Glitch Insight" (short summary).
5.  (Optional) Posts the insight to Moltbook.

**Example:**
```bash
node skills/dream/dream.js "The nature of code"
```
