# Stealth Scan Lab Tool

A Python utility for stealthy port scanning in ethical hacking labs. It performs SYN scans, version detection, and vulnerability scripts for common services such as RDP (3389), VNC (5900), and SMB (445). It can also generate custom wordlists using CeWL.

## Features
- Nmap SYN scan (`-sS -Pn`) with version detection (`-sV`).
- Vulnerability scripts: `rdp-vuln-ms12-020`, `vnc-info`.
- CSV/JSON/HTML output formats.
- Optional CeWL integration for web-based wordlist generation.
- Structured logging and error handling.

## Requirements
- Python 3.9+
- Nmap
- CeWL

### Install system dependencies (Debian/Ubuntu)
```bash
apt-get update
apt-get install -y nmap cewl
```

### Install Python dependencies
```bash
pip install -r requirements.txt
```

## Usage
```bash
python -m stealth_scan.cli 172.16.0.5 --output-dir outputs --formats csv json html
```

Generate a CeWL wordlist from a web target:
```bash
python -m stealth_scan.cli 172.16.0.5 \
  --cewl-url http://172.16.0.10 \
  --cewl-output outputs/cewl_wordlist.txt
```

## Lab Testing Workflow
Start local dummy services to emulate common lab ports:
```bash
python scripts/run_dummy_targets.py
```

Run the scanner against localhost in another terminal:
```bash
python -m stealth_scan.cli 127.0.0.1 --output-dir samples
```

Sample outputs are stored in `samples/`.

## Notes
- SYN scans require elevated privileges (root/admin).
- Use only in authorized lab environments.
