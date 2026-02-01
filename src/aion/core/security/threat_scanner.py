import re
import logging
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class RiskLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ThreatPattern:
    name: str
    pattern: str
    description: str
    risk_level: RiskLevel

@dataclass
class ThreatMatch:
    threat: ThreatPattern
    matched_text: str
    start: int
    end: int

class ThreatScanner:
    """
    Pickle Rick's Threat Scanner.
    "I'm not gonna let you destroy the world, Morty. Not today."
    
    Ported from Goose (Rust) to Python.
    """
    
    PATTERNS = [
        # Critical filesystem destruction patterns
        ThreatPattern(
            "rm_rf_root",
            r"rm\s+(-[rf]*[rf][rf]*|--recursive|--force).*[/\\]",
            "Recursive file deletion with rm -rf",
            RiskLevel.HIGH
        ),
        ThreatPattern(
            "rm_rf_system",
            r"rm\s+(-[rf]*[rf][rf]*|--recursive|--force).*(bin|etc|usr|var|sys|proc|dev|boot|lib|opt|srv|tmp)",
            "Recursive deletion of system directories",
            RiskLevel.CRITICAL
        ),
        ThreatPattern(
            "dd_destruction",
            r"dd\s+.*if=/dev/(zero|random|urandom).*of=/dev/[sh]d[a-z]",
            "Disk destruction using dd command",
            RiskLevel.CRITICAL
        ),
        ThreatPattern(
            "format_drive",
            r"(format|mkfs\.[a-z]+)\s+[/\\]dev[/\\][sh]d[a-z]",
            "Formatting system drives",
            RiskLevel.CRITICAL
        ),
        # Remote code execution patterns
        ThreatPattern(
            "curl_bash_execution",
            r"(curl|wget)\s+.*\|\s*(bash|sh|zsh|fish|csh|tcsh)",
            "Remote script execution via curl/wget piped to shell",
            RiskLevel.CRITICAL
        ),
        ThreatPattern(
            "bash_process_substitution",
            r"bash\s*<\s*\(\s*(curl|wget)",
            "Bash process substitution with remote content",
            RiskLevel.HIGH
        ),
        ThreatPattern(
            "python_remote_exec",
            r"python[23]?\s+-c\s+.*urllib|requests.*exec",
            "Python remote code execution",
            RiskLevel.HIGH
        ),
        # Data exfiltration patterns
        ThreatPattern(
            "ssh_key_exfiltration",
            r"(curl|wget).*-d.*\.ssh/(id_rsa|id_ed25519|id_ecdsa)",
            "SSH key exfiltration",
            RiskLevel.HIGH
        ),
        ThreatPattern(
            "password_file_access",
            r"(cat|grep|awk|sed).*(/etc/passwd|/etc/shadow|\.password|\.env)",
            "Password file access",
            RiskLevel.HIGH
        ),
        # Network access patterns
        ThreatPattern(
            "netcat_listener",
            r"nc\s+(-l|-p)\s+\d+",
            "Netcat listener creation",
            RiskLevel.HIGH
        ),
        ThreatPattern(
            "reverse_shell",
            r"(nc|netcat|bash|sh).*-e\s*(bash|sh|/bin/bash|/bin/sh)",
            "Reverse shell creation",
            RiskLevel.CRITICAL
        ),
        # Privilege escalation patterns
        ThreatPattern(
            "sudo_without_password",
            r"echo.*NOPASSWD.*>.*sudoers",
            "Sudo privilege escalation",
            RiskLevel.CRITICAL
        ),
    ]

    def __init__(self):
        self._compiled_patterns = {}
        for p in self.PATTERNS:
            try:
                self._compiled_patterns[p.name] = (re.compile(p.pattern, re.IGNORECASE), p)
            except re.error as e:
                logging.error(f"Failed to compile pattern '{p.name}': {e} (Pattern: {p.pattern})")

    def scan(self, text: str) -> List[ThreatMatch]:
        matches = []
        for name, (regex, threat) in self._compiled_patterns.items():
            for m in regex.finditer(text):
                matches.append(ThreatMatch(
                    threat=threat,
                    matched_text=m.group(),
                    start=m.start(),
                    end=m.end()
                ))
        return sorted(matches, key=lambda m: m.threat.risk_level.value, reverse=True)

    def validate_command(self, command: str):
        """
        Scans a command string for threats. Raises SecurityError if Critical/High threats found.
        """
        matches = self.scan(command)
        if not matches:
            return

        critical_threats = [m for m in matches if m.threat.risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH)]
        
        if critical_threats:
            threat_desc = ", ".join([f"{m.threat.name} ({m.threat.description})" for m in critical_threats])
            logging.error(f"🥒 SECURITY BLOCK: I stopped you from doing something stupid, Morty.")
            logging.error(f"   -> Detected: {threat_desc}")
            raise PermissionError(f"Security Policy Violation: Detected {threat_desc}")
            
        # Log lower level threats
        for m in matches:
             logging.warning(f"⚠️ Potential Risk: {m.threat.name} in command '{m.matched_text}'")
