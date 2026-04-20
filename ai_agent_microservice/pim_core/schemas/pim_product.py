from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PIMProductRecord(BaseModel):
    """Raw product record as received from the PIM system export.

    All fields are optional because PIM exports often contain empty strings or
    missing keys depending on the product category and data completeness.
    This model accepts the data exactly as the PIM sends it — no transformation here.
    """

    # Core identifiers
    productID: int = 0
    shortSku: str = ""
    reclassToSKU: str = ""
    vendorStyle: str = ""
    upc: str = ""
    isbnEan: str = ""

    # Names and descriptions
    productName: str = ""
    productDescription: str = ""
    posDescription: str = ""
    marketingCopy: str = ""
    bookTitle: str = ""
    notes: str = ""

    # Category and classification
    coordGroupDescription: str = ""
    coordGroup: str = ""
    coordGroupID: int = 0
    ipClass: int = 0
    ipStyle: int = 0
    deck: str = ""
    deckID: int = 0

    # Manufacturer / brand
    ipManufacturer: str = ""
    manufacturerName: str = ""
    webManufacturer: str = ""
    brand: str = ""
    brandID: int = 0
    ipVendorID: int = 0
    ipVendorNumber: int = 0
    vendorName: str = ""

    # Warranty
    warranty: str = ""
    asteaWarranty: str = ""
    vendorWarranty: str = ""

    # Pricing
    cost: float = 0.0
    lastVendorCost: float = 0.0
    suggestedRetailPrice: float = 0.0

    # Physical attributes
    packageDepth: str = ""
    packageWidth: str = ""
    packageHeight: str = ""
    ipColor: int = 0
    ipSize: int = 0
    deviceType: str = ""
    platform: str = ""
    productType: str = ""

    # Images
    image1: str = ""
    image2: str = ""
    image3: str = ""
    image4: str = ""

    # Generic attribute slots (populated per product category)
    attribute38: str = ""
    attribute39: str = ""
    attribute40: str = ""
    attribute41: str = ""
    attribute42: str = ""
    attribute43: str = ""
    attribute44: str = ""
    attribute45: str = ""
    attribute46: str = ""
    attribute47: str = ""

    # Copy slots
    copy1: str = ""
    copy2: str = ""
    copy3: str = ""
    copy4: str = ""

    # Status and metadata
    isActive: str = "Yes"
    isAnItemSet: bool = False
    filler: str = ""
    accountCode: str = ""

    # Dates (stored as strings — PIM format varies)
    dateCreated: str | None = None
    lastModifiedOn: str | None = None
    firstShipDate: str | None = None
    firstActivityDate: str | None = None
    streetDate: Any | None = None
    adEmbargo: Any | None = None

    # Book/media fields (not used for most product types)
    primaryAuthor: str = ""
    secondaryAuthor: str = ""
    thirdAuthor: str = ""
    bookFormat: str = ""
    edition: str = ""
    pageCount: int = 0
    previousIsbn: str = ""

    # Buyer / internal fields (not used for description generation)
    buyerID: int = 0
    buyerFirstName: str = ""
    buyerLastName: str = ""
    buyerIPUser: str = ""
    buyerAssociateID: str = ""

    # Distributor fields
    firstDistributorName: str = ""
    secondDistributorName: str = ""

    # Suggested / workflow fields
    suggestedPropertyValues: str = ""
    suggestedWebcategory: str = ""
    suggestedNotes: str = ""
    suggestedRetailPrice: float = 0.0

    # Reclass fields
    reclassToProductID: int = 0
    prodManufacturerID: int = 0

    model_config = {"extra": "allow"}
