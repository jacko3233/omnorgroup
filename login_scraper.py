import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def login_and_scrape(base_url, login_url, username, password, max_pages=50):
    """Logs into the website and recursively scrapes pages within the same domain."""
    session = requests.Session()
    # Attempt login
    payload = {
        "username": username,
        "password": password,
    }
    # Support common login keys; the user may need to adjust if the site uses different keys
    try:
        response = session.post(login_url, data=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Login failed: {e}")
        return

    visited = set()
    to_visit = [base_url]

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            page = session.get(url)
            page.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            continue

        print(f"Fetched {url} ({len(page.text)} bytes)")

        soup = BeautifulSoup(page.text, "html.parser")
        # print text from the page as example
        print(soup.get_text())

        for link in soup.find_all("a", href=True):
            href = urljoin(url, link["href"])
            if urlparse(href).netloc == urlparse(base_url).netloc:
                if href not in visited and href not in to_visit:
                    to_visit.append(href)


if __name__ == "__main__":
    base = "http://sitecert.info"  # starting page after login
    login_endpoint = "http://sitecert.info/login"
    login_and_scrape(base, login_endpoint, "jack23", "jack23")
