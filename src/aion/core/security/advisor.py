import re
import os
from pathlib import Path
from typing import List, Dict, Tuple

class SecurityAdvisor:
    """
    Implements the 'Insecure Defaults' skill from Trail of Bits.
    Scans for fail-open security configurations.
    """

    PATTERNS = [
        # Pattern: Fallback secrets (e.g., env.get('KEY') or 'default')
        (r"""getenv\s*\([^)]+\)\s*or\s*['"]""", "Critical: Fallback secret detected. App runs with weak secret if env var missing."),
        (r"""process\.env\.[A-Z_]+\s*\|\|\s*['"]""", "Critical: Hardcoded fallback secret in JS/TS."),
        
        # Pattern: Hardcoded credentials
        (r"""password.*=.*['"][^'"]{8,}['"]""", "High: Potential hardcoded password."),
        (r"""api[_-]?key.*=.*['"][^'"]+['"]""", "High: Potential hardcoded API key."),
        
        # Pattern: Weak defaults
        (r"""DEBUG.*=.*true""", "Medium: Debug mode enabled by default."),
        (r"""AUTH.*=.*false""", "High: Auth disabled by default."),
        (r"""CORS.*=.*[\*]""", "Medium: Permissive CORS default."),
        
        # Pattern: Weak Crypto
        (r"""(MD5|SHA1|DES|RC4|ECB)""", "High: Weak cryptographic algorithm detected.")
    ]

    def scan_file(self, file_path: Path) -> List[str]:
        issues = []
        try:
            content = file_path.read_text(errors='ignore')
            for pattern, msg in self.PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"{msg} (Pattern: {pattern})")
        except Exception:
            pass # Ignore unreadable files
        return issues

    def audit_directory(self, root_dir: Path) -> Dict[str, List[str]]:
        report = {}
        for root, _, files in os.walk(root_dir):
            if any(x in root for x in [".git", "__pycache__", "venv", "core/security"]):
                continue
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.env', '.json', '.yml', '.yaml')):
                    path = Path(root) / file
                    file_issues = self.scan_file(path)
                    if file_issues:
                        report[str(path)] = file_issues
        return report
