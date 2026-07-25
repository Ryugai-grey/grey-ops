import requests
from bs4 import BeautifulSoup

def load_payloads(filepath="payloads/xss.txt"):
    """Loads XSS payloads from the text file."""
    try:
        with open(filepath, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] Payload file not found: {filepath}")
        return []

def check_xss(form, payloads):
    """
    Fires XSS payloads at every input field.
    Detects reflected XSS by checking if the payload
    appears unescaped in the HTML response.
    """
    findings = []
    url = form["action"]
    method = form["method"]

    for payload in payloads:
        data = {}
        for field in form["inputs"]:
            if field["type"] in ["text", "search", "email", "password"]:
                data[field["name"]] = payload
            else:
                data[field["name"]] = field["value"]

        try:
            if method == "post":
                response = requests.post(url, data=data, timeout=5)
            else:
                response = requests.get(url, params=data, timeout=5)

            # Check if our payload is reflected back in the response
            # unescaped — meaning the app didn't sanitise it
            if payload in response.text:
                finding = {
                    "type": "Cross-Site Scripting (XSS)",
                    "severity": "HIGH",
                    "url": url,
                    "method": method.upper(),
                    "payload": payload,
                    "field": list(data.keys()),
                    "evidence": "Payload reflected unescaped in response",
                    "owasp": "A03:2021 - Injection / XSS",
                    "fix": "Encode all user output using html.escape(). Never reflect raw user input into HTML."
                }
                findings.append(finding)
                break

        except requests.exceptions.RequestException as e:
            print(f"[!] Request failed: {e}")
            continue

    return findings

def run(forms):
    """Main entry point called by scanner.py"""
    print("[*] Running XSS module...")
    payloads = load_payloads()
    if not payloads:
        return []

    all_findings = []
    seen = set()

    for form in forms:
        results = check_xss(form, payloads)
        for finding in results:
            key = f"{finding['url']}_{finding['type']}"
            if key not in seen:
                seen.add(key)
                all_findings.append(finding)
                print(f"  [HIGH] XSS confirmed — {finding['url']} — payload: {finding['payload']}")

    if not all_findings:
        print("  [INFO] No XSS vulnerabilities found")

    return all_findings