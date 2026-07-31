import os
from datetime import datetime
from pathlib import Path

import requests
from markdownify import markdownify as md


def require_env(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"{name} is empty or not set")
    return value


def main() -> None:
    domain = require_env("CONFLUENCE_DOMAIN")
    page_id = require_env("PAGE_ID")
    email = require_env("CONFLUENCE_EMAIL")
    api_token = require_env("CONFLUENCE_API_TOKEN")

    headers = {"Accept": "application/json"}
    auth = (email, api_token)

    # Probe identity endpoint first to verify credentials are valid.
    me_url = f"https://{domain}/wiki/rest/api/user/current"
    me_response = requests.get(me_url, auth=auth, headers=headers, timeout=30)
    print(f"Identity check: {me_url} -> HTTP {me_response.status_code}")
    if me_response.status_code >= 400:
        snippet = me_response.text[:500].replace("\n", " ")
        raise RuntimeError(
            "Confluence identity check failed with "
            f"HTTP {me_response.status_code}. Response snippet: {snippet}"
        )

    # Try v2 first; fallback to v1 content API for legacy IDs.
    v2_url = f"https://{domain}/wiki/api/v2/pages/{page_id}?body-format=storage"
    response = requests.get(v2_url, auth=auth, headers=headers, timeout=30)
    print(f"Fetch attempt (v2): {v2_url} -> HTTP {response.status_code}")

    if response.status_code == 404:
        v1_url = f"https://{domain}/wiki/rest/api/content/{page_id}?expand=body.storage"
        response = requests.get(v1_url, auth=auth, headers=headers, timeout=30)
        print(f"Fetch attempt (v1 fallback): {v1_url} -> HTTP {response.status_code}")

    if response.status_code >= 400:
        snippet = response.text[:800].replace("\n", " ")
        raise RuntimeError(
            "Confluence page fetch failed with "
            f"HTTP {response.status_code}. URL: {response.url}. "
            f"Response snippet: {snippet}"
        )

    data = response.json()
    page_title = data["title"]
    html_content = data["body"]["storage"]["value"]
    webui_path = data.get("_links", {}).get("webui", "")
    if webui_path:
        page_url = f"https://{domain}{webui_path}"
    else:
        page_url = f"https://{domain}/wiki/pages/{page_id}"

    markdown_content = md(html_content, heading_style="ATX")

    last_updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    final_content = "\n".join(
        [
            "---",
            'applyTo: "**"',
            "---",
            f"<!-- AUTO-GENERATED FROM CONFLUENCE — DO NOT EDIT MANUALLY -->",
            f"<!-- Source: {page_url} | Last synced: {last_updated} -->",
            "",
            f"# {page_title}",
            "",
            markdown_content,
            "",
        ]
    )

    output_file = Path(".github/instructions/development-standards.instructions.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(final_content, encoding="utf-8")

    print(f"Successfully fetched and converted: {page_title}")
    print(f"Written to: {output_file!s}")


if __name__ == "__main__":
    main()
