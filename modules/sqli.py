import requests

# Error messages that appear in responses when SQLi works
SQL_ERRORS = [
    "you have an error in your sql syntax",
    "warning: mysql",
    "unclosed quotation mark",
    "quoted string not properly terminated",
    "sqlite3.operationalerror",
    "sqlite3.databaseerror",
    "syntax error",
    "pg::syntaxerror",
    "microsoft ole db provider for sql server",
    "odbc microsoft access driver",
    "ora-01756",
    "invalid sql statement",
    "division by zero",
    "supplied argument is not a valid mysql",
]

def load_payloads(filepath="payloads/sqli.txt"):
    """Loads SQLi payloads from the text file."""
    try:
        with open(filepath, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] Payload file not found: {filepath}")
        return []

def check_sqli(form, payloads):
    """
    Takes a single form and fires every SQLi payload at it.
    Returns a list of confirmed vulnerabilities.
    """
    findings = []
    url = form["action"]
    method = form["method"]

    for payload in payloads:
        # Build the data dict — inject the payload into every field
        data = {}
        for field in form["inputs"]:
            if field["type"] in ["text", "search", "email", "password"]:
                data[field["name"]] = payload
            else:
                data[field["name"]] = field["value"]

        try:
            # Send the request
            if method == "post":
                response = requests.post(url, data=data, timeout=5)
            else:
                response = requests.get(url, params=data, timeout=5)

            # Check if any SQL error appears in the response
            response_lower = response.text.lower()
            for error in SQL_ERRORS:
                if error in response_lower:
                    finding = {
                        "type": "SQL Injection",
                        "severity": "CRITICAL",
                        "url": url,
                        "method": method.upper(),
                        "payload": payload,
                        "field": list(data.keys()),
                        "evidence": error,
                        "owasp": "A03:2021 - Injection",
                        "fix": "Use parameterised queries. Never concatenate user input into SQL strings."
                    }
                    findings.append(finding)
                    break  # one confirmation per payload is enough

        except requests.exceptions.RequestException as e:
            print(f"[!] Request failed: {e}")
            continue

    return findings

def run(forms):
    """
    Main entry point called by scanner.py
    Runs SQLi checks against all forms found by the crawler.
    """
    print("[*] Running SQL Injection module...")
    payloads = load_payloads()
    if not payloads:
        return []

    all_findings = []
    seen = set()  # prevent duplicate findings

    for form in forms:
        results = check_sqli(form, payloads)
        for finding in results:
            # Deduplicate — same URL + same type = same vulnerability
            key = f"{finding['url']}_{finding['type']}"
            if key not in seen:
                seen.add(key)
                all_findings.append(finding)
                print(f"  [CRITICAL] SQLi confirmed — {finding['url']} — payload: {finding['payload']}")

    if not all_findings:
        print("  [INFO] No SQL Injection vulnerabilities found")

    return all_findings