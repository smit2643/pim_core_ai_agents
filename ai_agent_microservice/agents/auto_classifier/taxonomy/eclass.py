from __future__ import annotations

import httpx
from lxml import etree


async def fetch_eclass_nodes(download_url: str, username: str, password: str) -> list[dict]:
    """Download eCl@ss XML and return flat list of level-4 class nodes."""
    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
        if username and password:
            resp = await client.get(download_url, auth=(username, password))
        else:
            resp = await client.get(download_url)
        resp.raise_for_status()

    root = etree.fromstring(resp.content)
    nodes: list[dict] = []

    for cls in root.iter("ClassificationClass"):
        code = cls.get("coded_name", "")
        level = int(cls.get("level", "4"))
        if level != 4 or not code:
            continue
        name_el = cls.find("preferred_name")
        name = ""
        if name_el is not None:
            label = name_el.find("label")
            name = label.text.strip() if label is not None and label.text else ""
        if not name:
            continue
        parent_code = code[:6] + "00"
        nodes.append({
            "code": code,
            "name": name,
            "parent_code": parent_code,
            "breadcrumb": name,
            "taxonomy_type": "eclass",
        })
    return nodes
