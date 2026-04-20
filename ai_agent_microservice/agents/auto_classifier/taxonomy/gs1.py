from __future__ import annotations

import io
import zipfile

import httpx
from lxml import etree

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.gs1.org/",
}


async def fetch_gs1_nodes(gpc_url: str) -> list[dict]:
    """Download GS1 GPC (ZIP or XML) and return flat list of brick-level nodes.

    Accepts a URL (https/http) or a local file path.
    GS1 releases are ZIPs containing one XML; we unzip automatically.
    """
    if gpc_url.startswith("http://") or gpc_url.startswith("https://"):
        xml_bytes = await _download(gpc_url)
    else:
        with open(gpc_url, "rb") as f:
            xml_bytes = f.read()

    if xml_bytes[:2] == b"PK":
        xml_bytes = _extract_xml_from_zip(xml_bytes)

    return _parse_gpc_xml(xml_bytes)


async def _download(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=120, follow_redirects=True, headers=_HEADERS) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content


def _extract_xml_from_zip(data: bytes) -> bytes:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        xml_names = [n for n in zf.namelist() if n.lower().endswith(".xml")]
        if not xml_names:
            raise ValueError("GS1 ZIP contains no XML file")
        xml_name = max(xml_names, key=lambda n: zf.getinfo(n).file_size)
        return zf.read(xml_name)


def _parse_gpc_xml(xml_bytes: bytes) -> list[dict]:
    root = etree.fromstring(xml_bytes)

    def _localname(el: etree._Element) -> str:
        return etree.QName(el.tag).localname

    def _child_text(el: etree._Element, child_localname: str) -> str:
        for child in el:
            if _localname(child) == child_localname:
                return (child.text or "").strip()
        return ""

    nodes: list[dict] = []
    for segment in root.iter():
        if _localname(segment) != "Segment":
            continue
        seg_name = _child_text(segment, "Text")
        for family in segment.iter():
            if _localname(family) != "Family":
                continue
            fam_name = _child_text(family, "Text")
            for klass in family.iter():
                if _localname(klass) != "Class":
                    continue
                cls_name = _child_text(klass, "Text")
                for brick in klass.iter():
                    if _localname(brick) != "Brick":
                        continue
                    brick_code = brick.get("Code", "")
                    brick_name = _child_text(brick, "Text")
                    if not brick_code or not brick_name:
                        continue
                    nodes.append({
                        "code": brick_code,
                        "name": brick_name,
                        "parent_code": segment.get("Code", ""),
                        "breadcrumb": f"{seg_name} > {fam_name} > {cls_name} > {brick_name}",
                        "taxonomy_type": "gs1",
                    })
    return nodes
