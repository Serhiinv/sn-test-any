import pytest
from urllib.parse import urljoin, urlparse

BASE_URL = "https://staging-lyonandturnbull.auctionfusion.com"

def is_internal_link(link):
    # Checks if the link is internal to the BASE_URL domain
    return link.startswith(BASE_URL)

def test_no_broken_internal_links(page):
    to_visit = set([BASE_URL])
    visited = set()
    broken_links = []

    while to_visit:
        current_url = to_visit.pop()
        if current_url in visited:
            continue
        print(f"Visiting: {current_url}")
        visited.add(current_url)
        try:
            page.goto(current_url, wait_until="domcontentloaded", timeout=20000)
        except Exception as e:
            broken_links.append(f"❌ Exception visiting {current_url}: {e}")
            continue

        links = page.eval_on_selector_all(
            "a[href]",
            "elements => elements.map(el => el.href)"
        )
        # Only collect internal links
        internal_links = [l for l in links if is_internal_link(l)]
        # Add new links to to_visit
        for link in internal_links:
            if link not in visited and link not in to_visit:
                to_visit.add(link)

        # Check all internal links on the current page
        for link in internal_links:
            try:
                response = page.request.get(link)
                status = response.status
                if status != 200:
                    broken_links.append(f"❌ Broken link on {current_url}: {link} (status {status})")
            except Exception as e:
                broken_links.append(f"❌ Exception loading link on {current_url}: {link} ({e})")

    if broken_links:
        print("\nBroken links found:")
        for broken in broken_links:
            print(broken)
    assert not broken_links, "Some internal links are broken!"
