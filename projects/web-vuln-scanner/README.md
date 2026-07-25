# 🔍 Web Vulnerability Scanner

A Python-based web vulnerability scanner built from scratch.
No Burp Suite. No SQLMap. Pure Python.

Autonomously crawls a target web application, discovers all
input vectors, fires a curated payload library at each one,
and generates a professional penetration test report in Markdown.

---

## ⚡ What It Does

| Phase | Action |
|-------|--------|
| Phase 1 — Crawl | Visits target, maps all pages, forms, and input fields |
| Phase 2 — Attack | Fires SQLi and XSS payloads at every discovered input |
| Phase 3 — Report | Auto-generates a dated professional pentest report |

---

## 🚀 Usage

\```bash
pip install -r requirements.txt
python scanner.py --target http://TARGET_IP:PORT
\```

---

## 📊 Sample Output

\```
[*] Target: http://127.0.0.1:5000
[*] Scan started: 21:36:03

[PHASE 1] Crawling target...
[+] Found form — Action: /login | Fields: ['username', 'password']
[*] Crawl complete — Visited 1 page(s), found 1 form(s)

[PHASE 2] Running vulnerability modules...
[*] Running SQL Injection module...
  [CRITICAL] SQLi confirmed — /login — payload: ') OR ('1'='1
[*] Running XSS module...
  [INFO] No XSS vulnerabilities found

==================================================
  SCAN COMPLETE — Total vulnerabilities found: 1
  [CRITICAL] SQL Injection — http://127.0.0.1:5000/login
==================================================

[PHASE 3] Generating report...
[+] Report saved: reports/scan-2026-07-25_21-36-04.md
\```

---

## 📁 Project Structure

\```
web-vuln-scanner/
├── scanner.py          # main engine
├── crawler.py          # discovers all pages and forms
├── modules/
│   ├── __init__.py
│   ├── sqli.py         # SQL injection module
│   └── xss.py          # XSS module
├── payloads/
│   ├── sqli.txt        # 20+ SQLi payloads
│   ├── xss.txt         # 15+ XSS payloads
│   └── traversal.txt   # directory traversal payloads
├── reports/            # auto-generated scan reports
└── requirements.txt
\```

---

## 🧠 How Detection Works

**SQL Injection**
Fires payloads into every input field and checks the HTTP
response for database error signatures — sqlite3.OperationalError,
MySQL syntax errors, and similar strings. Confirmed if found.

**Cross-Site Scripting (XSS)**
Fires script payloads into every input field and checks whether
the payload is reflected back in the HTML response unescaped.
Unescaped reflection confirms reflected XSS.

---

## 🛡️ OWASP Top 10 Coverage

| OWASP ID | Category | Tested |
|----------|----------|--------|
| A03:2021 | Injection — SQL | ✅ |
| A03:2021 | Injection — XSS | ✅ |
| A05:2021 | Security Misconfiguration | ✅ |

---

## 📄 Sample Report

A real scan report generated against a deliberately vulnerable
Flask application is in the [reports/](./reports/) folder.

Each report includes:
- Executive summary with severity counts
- Per-vulnerability details with exact payload used
- OWASP category mapping
- Remediation advice for every finding

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-Library-orange?style=flat)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-HTML_Parser-green?style=flat)
![OWASP](https://img.shields.io/badge/OWASP_Top_10-Aligned-red?style=flat)
![Kali](https://img.shields.io/badge/Tested_On-Kali_Linux-557C94?style=flat&logo=kali-linux&logoColor=white)

---

## 🔬 Lab Environment

Built and tested against a deliberately vulnerable Flask
application with real SQLi and XSS vulnerabilities planted
intentionally to validate scanner accuracy.

- Target: Python + Flask + SQLite
- Attack machine: Kali Linux VM
- Dev machine: Windows 10/11

---

## ⚠️ Legal Disclaimer

For educational purposes only.
Only scan systems you own or have explicit written permission
to test. Unauthorised scanning is illegal.

---

*Part of a structured cybersecurity learning journey —
[github.com/Ryugai-grey](https://github.com/Ryugai-grey)*
