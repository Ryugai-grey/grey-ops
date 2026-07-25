import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def crawl(target_url, max_pages=10):
    """
    Visits the target URL, finds all links and forms,
    and returns a list of attack surfaces to test.
    """

    visited = set()
    to_visit = [target_url]
    forms_found = []

    print(f"\n[*] Starting crawler on: {target_url}")

    while to_visit and len(visited) < max_pages:

        current_url = to_visit.pop(0)

        if current_url in visited:
            continue

        try:
            response = requests.get(current_url, timeout=5)
            visited.add(current_url)
            print(f"[*] Crawling: {current_url} — Status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"[!] Could not reach {current_url} — {e}")
            continue

        # Parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all forms on this page
        forms = soup.find_all("form")
        for form in forms:
            form_details = get_form_details(form, current_url)
            forms_found.append(form_details)
            print(f"[+] Found form — Action: {form_details['action']} | Method: {form_details['method']} | Fields: {[f['name'] for f in form_details['inputs']]}")

        # Find all internal links and add to queue
        for link in soup.find_all("a", href=True):
            full_url = urljoin(current_url, link["href"])
            if is_same_domain(target_url, full_url) and full_url not in visited:
                to_visit.append(full_url)

    print(f"\n[*] Crawl complete — Visited {len(visited)} page(s), found {len(forms_found)} form(s)\n")
    return forms_found


def get_form_details(form, page_url):
    """
    Extracts everything useful from a single HTML form.
    Returns a dict with the action URL, method, and all input fields.
    """

    details = {}

    # Where does the form submit to?
    action = form.attrs.get("action", "")
    details["action"] = urljoin(page_url, action)

    # GET or POST?
    details["method"] = form.attrs.get("method", "get").lower()

    # What input fields does it have?
    inputs = []
    for input_tag in form.find_all(["input", "textarea"]):
        input_name = input_tag.attrs.get("name")
        input_type = input_tag.attrs.get("type", "text")
        input_value = input_tag.attrs.get("value", "test")

        if input_name:
            inputs.append({
                "name": input_name,
                "type": input_type,
                "value": input_value
            })

    details["inputs"] = inputs
    return details


def is_same_domain(base_url, check_url):
    """
    Makes sure we only follow links that stay on the target site.
    Prevents the crawler from wandering off to external sites.
    """
    return urlparse(base_url).netloc == urlparse(check_url).netloc


# Quick test — run this file directly to verify crawler works
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = "http://127.0.0.1:5000"

    results = crawl(target)

    print("=" * 50)
    print(f"FORMS DISCOVERED: {len(results)}")
    print("=" * 50)
    for i, form in enumerate(results, 1):
        print(f"\nForm {i}:")
        print(f"  Action : {form['action']}")
        print(f"  Method : {form['method']}")
        print(f"  Fields : {[f['name'] for f in form['inputs']]}")
