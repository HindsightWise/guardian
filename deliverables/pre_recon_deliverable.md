# Pre-Reconnaissance Deliverable (Project Glossopetrae)

**Target:** https://juice-shop.herokuapp.com
**Date:** 2026-02-07
**Method:** Native Tool Execution (Node.js)

## 1. Executive Summary
The target appears to be a standard web application hosted on Heroku/AWS infrastructure.
- **Hosting:** Heroku (AWS eu-west-1 region verified via rDNS).
- **Subdomains:** None discovered (likely using platform-provided subdomain `juice-shop`).
- **Open Ports:** 80 (HTTP), 443 (HTTPS).

## 2. Tool Output

### 2.1 Subdomain Discovery (Subfinder)
- **Command:** `subfinder -d juice-shop.herokuapp.com`
- **Result:** 0 subdomains found.

### 2.2 Network Scanning (Nmap)
- **Command:** `nmap -F juice-shop.herokuapp.com` (Fast Scan)
- **Status:** Host is up (0.19s latency).
- **Open Ports:**
    - `80/tcp` (http)
    - `443/tcp` (https)
- **Infrastructure Notes:**
    - Resolved IP: `46.137.15.86`
    - rDNS: `ec2-46-137-15-86.eu-west-1.compute.amazonaws.com`

## 3. Pending Analysis (Code Review)
**Status:** Ready for Agentic Analysis.
The source code is available locally for deep inspection.
Recommended Next Steps:
1.  Run `skills/pentest/analyze_code.js` (To be implemented).
2.  Map authentication endpoints and API routes from source.
