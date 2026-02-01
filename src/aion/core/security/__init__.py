# aion/core/security/__init__.py
import subprocess
import logging
import time
import shutil
from pathlib import Path
from .auditor import SecurityAuditor
from .path_guard import PathGuard
from .threat_scanner import ThreatScanner
from .advisor import SecurityAdvisor

class SecurityProtocol:
    """
    Enforces security boundaries for the AION Daemon.
    Primary directive: Ensure traffic flows through the secure tunnel (WARP) and local hygiene is maintained.
    """
    
    _path_guard = None
    _threat_scanner = ThreatScanner()
    _advisor = SecurityAdvisor()

    @staticmethod
    def _check_warp_status() -> bool:
        """Checks if Cloudflare WARP is connected."""
        if not shutil.which("warp-cli"):
            logging.warning("⚠️ Security Warning: 'warp-cli' not found. Cannot verify VPN status.")
            return False

        try:
            result = subprocess.run(
                ["warp-cli", "status"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            output = result.stdout.lower()
            if "connected" in output and "disconnected" not in output:
                return True
            return False
        except Exception as e:
            logging.error(f"❌ Security Check Error: {e}")
            return False

    @staticmethod
    def ensure_secure_connection(root_path: Path = Path(".")):
        """
        Blocking call that refuses to let the daemon start unless WARP is active.
        Also runs the Pickle Rick System Audit.
        """
        logging.info("🛡️ Initiating Security Protocol: WARP Check...")
        
        while not SecurityProtocol._check_warp_status():
            logging.error("⛔ FATAL: Cloudflare WARP is NOT connected. The daemon is vulnerable.")
            logging.info("   -> Please run 'warp-cli connect' or check your network.")
            logging.info("   -> Retrying in 5 seconds...")
            time.sleep(5)
        
        logging.info("✅ Security Protocol Verified: WARP Tunnel Active.")
        
        # Initialize PathGuard
        SecurityProtocol._path_guard = PathGuard(root_path)
        
        # Run Audit
        SecurityAuditor.audit_system(root_path)
        
        # Run Static Code Analysis
        logging.info("🔬 Running Static Security Analysis...")
        issues = SecurityProtocol.run_codebase_audit(root_path)
        if issues:
            logging.warning(f"⚠️  Found {len(issues)} files with potential security risks:")
            for file, problems in issues.items():
                logging.warning(f"   📄 {file}:")
                for prob in problems:
                    logging.warning(f"      - {prob}")
        else:
            logging.info("✅ Static Analysis Passed: No obvious insecurities found.")

    @staticmethod
    def validate_path(path: str | Path) -> Path:
        """Proxies to the active PathGuard instance."""
        if not SecurityProtocol._path_guard:
            raise RuntimeError("SecurityProtocol not initialized. Call ensure_secure_connection() first.")
        return SecurityProtocol._path_guard.validate_path(path)

    @staticmethod
    def validate_command(command: str):
        """
        Scans a shell command for known threat patterns (rm -rf /, reverse shells, etc).
        Raises PermissionError if a threat is detected.
        """
        SecurityProtocol._threat_scanner.validate_command(command)

    @staticmethod
    def run_codebase_audit(root_path: Path) -> dict:
        """
        Runs a static analysis on the codebase to find insecure defaults.
        """
        return SecurityProtocol._advisor.audit_directory(root_path)