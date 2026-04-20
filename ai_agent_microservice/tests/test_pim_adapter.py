from __future__ import annotations

import pytest

from pim_core.adapters.pim_adapter import pim_record_to_product
from pim_core.schemas.pim_product import PIMProductRecord


def _make_record(**kwargs) -> PIMProductRecord:
    """Return a minimal valid PIM record, overriding fields via kwargs."""
    defaults = {
        "productID": 705517,
        "shortSku": "969196",
        "productName": "MACSTUDIO E25 M4M/64/1TB",
        "coordGroupDescription": "APPLE DESKTOP SYSTEMS    ",
        "ipManufacturer": "APPLE",
        "productDescription": "MACSTUDIO E25 M4M/64/1TB",
        "warranty": "1 year",
        "asteaWarranty": "1YearVendor",
        "vendorStyle": "15098309",
    }
    defaults.update(kwargs)
    return PIMProductRecord(**defaults)


def test_adapter_maps_product_id_as_string():
    product = pim_record_to_product(_make_record(productID=705517))
    assert product.id == "705517"


def test_adapter_maps_sku():
    product = pim_record_to_product(_make_record(shortSku="969196"))
    assert product.sku == "969196"


def test_adapter_maps_product_name():
    product = pim_record_to_product(_make_record(productName="MACSTUDIO E25 M4M/64/1TB"))
    assert product.name == "MACSTUDIO E25 M4M/64/1TB"


def test_adapter_strips_trailing_spaces_from_category():
    product = pim_record_to_product(_make_record(coordGroupDescription="APPLE DESKTOP SYSTEMS    "))
    assert product.category == "APPLE DESKTOP SYSTEMS"


def test_adapter_maps_manufacturer_as_brand():
    product = pim_record_to_product(_make_record(ipManufacturer="APPLE"))
    assert product.attributes.brand == "APPLE"


def test_adapter_includes_warranty_in_additional():
    product = pim_record_to_product(_make_record(warranty="1 year"))
    assert product.attributes.additional["warranty"] == "1 year"


def test_adapter_includes_astea_warranty_in_additional():
    product = pim_record_to_product(_make_record(asteaWarranty="1YearVendor"))
    assert product.attributes.additional["astea_warranty"] == "1YearVendor"


def test_adapter_includes_vendor_part_number_in_additional():
    product = pim_record_to_product(_make_record(vendorStyle="15098309"))
    assert product.attributes.additional["vendor_part_number"] == "15098309"


def test_adapter_excludes_empty_additional_fields():
    product = pim_record_to_product(_make_record(upc="", deviceType="", platform=""))
    assert "upc" not in product.attributes.additional
    assert "device_type" not in product.attributes.additional
    assert "platform" not in product.attributes.additional


def test_adapter_filters_empty_image_urls():
    product = pim_record_to_product(_make_record(image1="", image2="", image3="", image4=""))
    assert product.image_urls == []


def test_adapter_keeps_non_empty_image_urls():
    product = pim_record_to_product(_make_record(
        image1="https://cdn.example.com/img1.jpg",
        image2="",
        image3="https://cdn.example.com/img3.jpg",
        image4="",
    ))
    assert product.image_urls == [
        "https://cdn.example.com/img1.jpg",
        "https://cdn.example.com/img3.jpg",
    ]


def test_adapter_skips_existing_description_when_same_as_product_name():
    """productDescription is usually just the product name — skip it to avoid redundancy."""
    product = pim_record_to_product(_make_record(
        productName="MACSTUDIO E25 M4M/64/1TB",
        productDescription="MACSTUDIO E25 M4M/64/1TB",
        marketingCopy="",
        posDescription="MACSTUDIO E25 M4M/64/1TB",
    ))
    assert product.existing_description is None


def test_adapter_uses_marketing_copy_as_existing_description_when_available():
    product = pim_record_to_product(_make_record(
        productName="MACSTUDIO E25 M4M/64/1TB",
        marketingCopy="The ultimate desktop workstation powered by Apple M4 Max.",
    ))
    assert product.existing_description == "The ultimate desktop workstation powered by Apple M4 Max."


def test_adapter_brand_is_none_when_manufacturer_empty():
    product = pim_record_to_product(_make_record(ipManufacturer=""))
    assert product.attributes.brand is None


def test_adapter_includes_non_empty_attribute_slots():
    product = pim_record_to_product(_make_record(attribute38="Silver", attribute39=""))
    assert product.attributes.additional["attribute38"] == "Silver"
    assert "attribute39" not in product.attributes.additional


def test_adapter_includes_device_type_when_set():
    product = pim_record_to_product(_make_record(deviceType="Desktop"))
    assert product.attributes.additional["device_type"] == "Desktop"


def test_adapter_includes_platform_when_set():
    product = pim_record_to_product(_make_record(platform="macOS"))
    assert product.attributes.additional["platform"] == "macOS"
