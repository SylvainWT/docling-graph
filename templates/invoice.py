"""
Pydantic templates for Invoice extraction.

This file is self-contained and has no external template dependencies.
It includes all necessary sub-models and provides examples for each field.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date

# --- Reusable Component: MonetaryAmount ---
class MonetaryAmount(BaseModel):
    """
    A component model to represent a monetary value with its currency.
    No graph_id_fields, as it's a value object.
    """
    value: float = Field(
        ...,
        description="The numeric value of the amount",
        examples=[150.00, 29.99, 1234.56]
    )
    currency: Optional[str] = Field(
        None,
        description="The ISO 4217 currency code",
        examples=["EUR", "USD", "GBP"]
    )

    def __str__(self):
        return f"{self.value} {self.currency or ''}".strip()

# --- Reusable Component: Address ---
class Address(BaseModel):
    """
    A flexible, generic model for a physical address.
    It's treated as a component, so it has no graph_id_fields.
    """
    street_address: Optional[str] = Field(
        None,
        description="Street name and number",
        examples=["55 Rue du Faubourg Saint-Honoré", "100 Main Street"]
    )
    city: Optional[str] = Field(
        None,
        description="City",
        examples=["Paris", "New York"]
    )
    state_or_province: Optional[str] = Field(
        None,
        description="State, province, or region",
        examples=["Île-de-France", "NY"]
    )
    postal_code: Optional[str] = Field(
        None,
        description="Postal or ZIP code",
        examples=["75008", "10001"]
    )
    country: Optional[str] = Field(
        None,
        description="Country",
        examples=["France", "USA"]
    )

    def __str__(self):
        parts = [self.street_address, self.city, self.state_or_province, self.postal_code, self.country]
        return ", ".join(p for p in parts if p)

# --- Reusable Entity: Organization ---
class Organization(BaseModel):
    """
    A generic model for any organization (vendor, customer, etc.).
    Its name is its unique identifier in the graph.
    """
    model_config = ConfigDict(graph_id_fields=['name'])
    
    name: str = Field(
        ...,
        description="The legal name of the organization",
        examples=["TechCorp SAS", "Global Solutions Ltd."]
    )
    phone: Optional[str] = Field(
        None,
        description="Contact phone number",
        examples=["+33 1 23 45 67 89", "+1 212 555 1234"]
    )
    email: Optional[str] = Field(
        None,
        description="Contact email address",
        examples=["contact@techcorp.fr", "billing@globalsolutions.com"]
    )
    website: Optional[str] = Field(
        None,
        description="Official website",
        examples=["www.techcorp.fr", "globalsolutions.com"]
    )
    tax_id: Optional[str] = Field(
        None,
        description="Tax ID, VAT ID, or other official identifier",
        examples=["FR123456789", "EIN 98-7654321"]
    )
    
    # An organization can have one or more addresses
    addresses: List[Address] = Field(
        default_factory=list,
        description="List of physical addresses for the organization"
    )
    
    def __str__(self):
        return self.name

# --- Reusable Component: LineItem ---
class LineItem(BaseModel):
    """
    A single line item on the invoice.
    It's a component, so no graph_id_fields.
    """
    description: str = Field(
        ...,
        description="Description of the product or service",
        examples=["Monthly Software Subscription - Pro Plan", "Consulting Services (10.5 hours)"]
    )
    quantity: Optional[float] = Field(
        1.0,
        description="Quantity of the item",
        examples=[1.0, 10.5, 50.0]
    )
    unit_price: Optional[MonetaryAmount] = Field(
        None,
        description="Price per unit"
    )
    line_total: Optional[MonetaryAmount] = Field(
        None,
        description="Total amount for this line (quantity * unit_price)"
    )
    sku_or_item_code: Optional[str] = Field(
        None,
        description="Stock Keeping Unit or item code",
        examples=["SUB-001-PRO", "SRV-CONS-HR"]
    )
    tax_rate: Optional[float] = Field(
        None,
        description="Tax rate applied to this line item (as a percentage)",
        examples=[20.0, 5.5, 8.25]
    )
    
    def __str__(self):
        return self.description

# --- Reusable Component: TaxDetail ---
class TaxDetail(BaseModel):
    """A component for detailing a specific tax applied to the whole invoice."""
    description: str = Field(
        ...,
        description="Type of tax",
        examples=["TVA", "Sales Tax", "VAT"]
    )
    rate: Optional[float] = Field(
        None,
        description="Tax rate as a percentage",
        examples=[20.0, 8.25]
    )
    amount: Optional[MonetaryAmount] = Field(
        None,
        description="The total amount of this tax"
    )

# --- Root Document Model: Invoice ---
class Invoice(BaseModel):
    """
    The root model for a generic invoice, receipt, or bill.
    It's identified by its invoice number.
    """
    model_config = ConfigDict(graph_id_fields=['invoice_number'])
    
    invoice_number: str = Field(
        ...,
        description="Unique identifier for the invoice",
        examples=["INV-2024-00123", "F24-10-589", "8373-10-2024"]
    )
    invoice_date: Optional[date] = Field(
        None,
        description="Date the invoice was issued (YYYY-MM-DD)",
        examples=["2024-10-23"]
    )
    due_date: Optional[date] = Field(
        None,
        description="Date payment is due (YYYY-MM-DD)",
        examples=["2024-11-22"]
    )
    payment_terms: Optional[str] = Field(
        None,
        description="Payment terms (e.g., Net 30, Due on receipt)",
        examples=["Net 30", "Due on receipt", "NET 15"]
    )
    
    # Using the generic Organization model for both parties.
    issuer: Optional[Organization] = Field(
        None,
        description="The organization issuing the invoice (seller, vendor)"
    )
    recipient: Optional[Organization] = Field(
        None,
        description="The organization receiving the invoice (buyer, customer)"
    )
    
    # This will be automatically detected as a list of edges to LineItem nodes.
    line_items: List[LineItem] = Field(
        default_factory=list
    )
    
    # Using MonetaryAmount for all financial fields
    subtotal: Optional[MonetaryAmount] = Field(
        None,
        description="The total amount before taxes and discounts"
    )
    total_tax_amount: Optional[MonetaryAmount] = Field(
        None,
        description="The total sum of all taxes"
    )
    total_amount: Optional[MonetaryAmount] = Field(
        None,
        description="The final amount due, including all taxes and fees"
    )
    amount_paid: Optional[MonetaryAmount] = Field(
        None,
        description="The amount already paid",
        examples=[0.0]
    )
    amount_due: Optional[MonetaryAmount] = Field(
        None,
        description="The remaining balance to be paid (total - paid)"
    )
    
    # List of component nodes for tax details
    tax_details: List[TaxDetail] = Field(
        default_factory=list,
        description="A list of all taxes applied (e.g., VAT 20%)"
    )
    
    notes: Optional[str] = Field(
        None,
        description="Any additional notes or comments on the invoice",
        examples=["Thank you for your business!", "Please remit payment to..."]
    )

    def __str__(self):
        return f"Invoice {self.invoice_number}"

