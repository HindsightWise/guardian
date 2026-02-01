import os
import logging
import stat
from pathlib import Path
import subprocess
import shutil

class SecurityAuditor:
    """
    The Pickle Rick Security Auditor.
    "I turned myself into a security audit, Morty! I'm Audit Rick!"
    """

    @staticmethod
    def audit_system(root_path: Path):
        logging.info("🥒 Audit Rick: Initiating System Scan... *burp*")
        
        issues = []

        # 1. WARP Check (Network)
        if not SecurityAuditor._check_warp():
            issues.append("CRITICAL: Cloudflare WARP is OFF. You're naked on the internet, Morty.")

        # 2. Env Var Check (Secrets)
        required_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OPENCLAW_GATEWAY_TOKEN"]
        found_vars = [v for v in required_vars if os.getenv(v)]
        if not found_vars:
            issues.append("WARN: No major API keys found in environment. What are we gonna do, calculate pi manually?")

        # 3. File Permissions (.env)
        env_path = root_path / ".env"
        if env_path.exists():
            perms = env_path.stat().st_mode
            if perms & stat.S_IRWXO: # Readable/Writable by others
                issues.append(f"CRITICAL: .env is world-readable ({oct(perms)}). Anyone can steal your secrets, you Jerry.")
        
        # 4. Git Status (Hygiene)
        if (root_path / ".git").exists():
            if not SecurityAuditor._is_git_clean(root_path):
                issues.append("WARN: Git directory is dirty. Commit your code, Morty. Stop leaving slop everywhere.")

        # Report
        if issues:
            logging.warning("🥒 Audit Rick found some garbage:")
            for issue in issues:
                logging.warning(f"   - {issue}")
            
            # If critical, maybe we should stop? For now, we scream.
            if any("CRITICAL" in i for i in issues):
                logging.error("🥒 I'm not angry, I'm just disappointed. Fix the criticals.")
        else:
            logging.info("🥒 Audit Rick: System clean. Wubba Lubba Dub Dub!")

    @staticmethod
    def _check_warp() -> bool:
        """Checks if Cloudflare WARP is connected."""
        if not shutil.which("warp-cli"):
            return False # Assume unsafe if we can't check
        try:
            result = subprocess.run(
                ["warp-cli", "status"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return "connected" in result.stdout.lower() and "disconnected" not in result.stdout.lower()
        except Exception:
            return False

    @staticmethod
    def _is_git_clean(path: Path) -> bool:
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                cwd=path,
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return not result.stdout.strip() # Empty means clean
        except Exception:
            return False
