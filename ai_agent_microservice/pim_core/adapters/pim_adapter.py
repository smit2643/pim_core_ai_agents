from __future__ import annotations

from pim_core.schemas.pim_product import PIMProductRecord
from pim_core.schemas.product import Product, ProductAttributes


def pim_record_to_product(record: PIMProductRecord) -> Product:
    """Convert a raw PIM product record into the normalised Product schema.

    Field mapping:
        productID             → id   (cast to str)
        shortSku              → sku
        productName           → name
        coordGroupDescription → category  (trailing spaces stripped)
        ipManufacturer        → attributes.brand
        productDescription    → existing_description (preferred)
        marketingCopy         → existing_description fallback
        posDescription        → existing_description final fallback
        warranty              → attributes.additional["warranty"]
        asteaWarranty         → attributes.additional["astea_warranty"]
        vendorStyle           → attributes.additional["vendor_part_number"]
        upc                   → attributes.additional["upc"]
        deviceType            → attributes.additional["device_type"]
        platform              → attributes.additional["platform"]
        productType           → attributes.additional["product_type"]
        image1–image4         → image_urls  (empty strings filtered out)
        attribute38–attribute47 → attributes.additional  (non-empty only)
    """
    # --- existing description: pick the most informative non-empty value ---
    existing_description: str | None = None
    for candidate in (
        record.marketingCopy,
        record.productDescription,
        record.posDescription,
    ):
        stripped = candidate.strip()
        # Skip values that are just repetitions of the product name (adds no value)
        if stripped and stripped.upper() != record.productName.strip().upper():
            existing_description = stripped
            break

    # --- additional attributes: only include non-empty values ---
    additional: dict[str, str] = {}

    _add_if_set(additional, "warranty", record.warranty)
    _add_if_set(additional, "astea_warranty", record.asteaWarranty)
    _add_if_set(additional, "vendor_part_number", record.vendorStyle)
    _add_if_set(additional, "upc", record.upc)
    _add_if_set(additional, "device_type", record.deviceType)
    _add_if_set(additional, "platform", record.platform)
    _add_if_set(additional, "product_type", record.productType)

    # Generic attribute slots — included when non-empty
    for slot_num in range(38, 48):
        value = getattr(record, f"attribute{slot_num}", "").strip()
        if value:
            additional[f"attribute{slot_num}"] = value

    # --- image URLs: filter out empty strings ---
    image_urls = [
        url for url in (record.image1, record.image2, record.image3, record.image4)
        if url.strip()
    ]

    return Product(
        id=str(record.productID),
        sku=record.shortSku.strip(),
        name=record.productName.strip(),
        category=record.coordGroupDescription.strip(),
        attributes=ProductAttributes(
            brand=record.ipManufacturer.strip() or None,
            additional=additional,
        ),
        existing_description=existing_description,
        image_urls=image_urls,
    )


def _add_if_set(target: dict[str, str], key: str, value: str) -> None:
    """Add value to dict only when it is a non-empty, non-whitespace string."""
    stripped = value.strip()
    if stripped:
        target[key] = stripped
