from __future__ import annotations

import yaml


def load_custom_nodes(yaml_path: str) -> list[dict]:
    """Load custom taxonomy from a YAML file.

    Expected format:
      - code: "ELEC-001"
        name: "Resistors"
        parent_code: "ELEC"
        breadcrumb: "Electronics > Passive Components > Resistors"
    """
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, list):
        raise ValueError(f"Custom taxonomy YAML must be a list, got {type(data)}")

    return [
        {
            "code": str(item["code"]),
            "name": str(item["name"]),
            "parent_code": str(item.get("parent_code", "")),
            "breadcrumb": str(item.get("breadcrumb", item["name"])),
            "taxonomy_type": "custom",
        }
        for item in data
    ]
