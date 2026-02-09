/**
 * Antigravity Bridge for Glossopetrae
 * Allows the Agent to invoke the skill via CLI.
 */
import { GlossopetraeSkill } from "../skills/glossopetrae/src/skill/GlossopetraeSkill.js";

const [, , command, ...args] = process.argv;

async function main() {
  try {
    switch (command) {
      case "forge":
        const name = args[0] || "AntigravityLang";
        // Use 'tactical' preset for speed (Minimal lexicon)
        const lang = await GlossopetraeSkill.forgeStealthLanguage("tactical", name);
        console.log(
          JSON.stringify(
            {
              name: lang.info.name,
              phonology: lang.language.phonology.inventory,
              example: lang.translate("The guardian watches the stars."),
            },
            null,
            2,
          ),
        );
        break;

      case "translate":
        const text = args.join(" ");
        // Use 'tactical' preset for speed
        const tLang = await GlossopetraeSkill.forgeStealthLanguage("tactical", "antigravity-seed");
        console.log(tLang.translate(text));
        break;

      case "skillstone":
        const sLang = await GlossopetraeSkill.forgeStealthLanguage("tactical", "antigravity-prime");
        console.log(sLang.generateStone());
        break;

      default:
        console.log(
          "Usage: node scripts/antigravity_glossopetrae.mjs [forge|translate|skillstone] [args]",
        );
    }
  } catch (e) {
    console.error("Error:", e.message);
  }
}

main();
