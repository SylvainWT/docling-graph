"""
Pydantic templates for ID Card extraction.

This file is self-contained and has no external template dependencies.
It includes all necessary sub-models and provides examples for each field.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import date

# --- Reusable Component: Address ---
class Address(BaseModel):
    """
    A flexible, generic model for a physical address.
    It's treated as a component, so it has no graph_id_fields.
    Its ID will be a hash of its content, making it unique to its context.
    """
    street_address: Optional[str] = Field(
        None,
        description="Street name and number",
        examples=["123 Rue de la Paix", "90 Boulevard Voltaire"]
    )
    city: Optional[str] = Field(
        None,
        description="City",
        examples=["Paris", "Lyon"]
    )
    state_or_province: Optional[str] = Field(
        None,
        description="State, province, or region",
        examples=["Île-de-France"]
    )
    postal_code: Optional[str] = Field(
        None,
        description="Postal or ZIP code",
        examples=["75001", "69002"]
    )
    country: Optional[str] = Field(
        None,
        description="Country",
        examples=["France"]
    )

    def __str__(self):
        parts = [self.street_address, self.city, self.state_or_province, self.postal_code, self.country]
        return ", ".join(p for p in parts if p)

# --- Reusable Entity: Person ---
class Person(BaseModel):
    """
    A generic model for a person.
    A person is uniquely identified by their full name and date of birth.
    """
    model_config = ConfigDict(graph_id_fields=['first_name', 'last_name', 'date_of_birth'])
    
    first_name: Optional[str] = Field(
        None,
        description="The person's given name(s)",
        examples=["Marie", "Pierre", "Jean-Jacques"]
    )
    last_name: Optional[str] = Field(
        None,
        description="The person's family name (surname)",
        examples=["Dupont", "Martin"]
    )
    date_of_birth: Optional[date] = Field(
        None,
        description="Date of birth in YYYY-MM-DD format",
        examples=["1990-05-15"]
    )
    place_of_birth: Optional[str] = Field(
        None,
        description="City and/or country of birth",
        examples=["Paris", "Marseille (France)"]
    )
    gender: Optional[str] = Field(
        None,
        description="Gender or sex of the person",
        examples=["F", "M", "Female", "Male"]
    )
    nationality: Optional[str] = Field(
        None,
        description="Nationality of the person",
        examples=["Française", "French"]
    )
    phone: Optional[str] = Field(
        None,
        description="Contact phone number",
        examples=["+33 6 12 34 56 78"]
    )
    email: Optional[str] = Field(
        None,
        description="Contact email address",
        examples=["marie.dupont@email.fr"]
    )
    
    # A person can have one or more addresses
    addresses: List[Address] = Field(
        default_factory=list,
        description="List of physical addresses (e.g., home, work)"
    )
    
    def __str__(self):
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p)

# --- Root Document Model: IDCard ---
class IDCard(BaseModel):
    """
    A model for an identification document.
    It is uniquely identified by its document number.
    """
    model_config = ConfigDict(graph_id_fields=['document_number'])
    
    document_type: str = Field(
        "ID Card",
        description="Type of document (e.g., ID Card, Passport, Driver's License)",
        examples=["Carte Nationale d'Identité", "Passeport"]
    )
    document_number: str = Field(
        ...,
        description="The unique identifier for the document",
        examples=["23AB12345", "19XF56789"]
    )
    issuing_country: Optional[str] = Field(
        None,
        description="The country that issued the document (e.g., 'France', 'République Française')",
        examples=["France", "USA"]
    )
    issue_date: Optional[date] = Field(
        None,
        description="Date the document was issued, in YYYY-MM-DD format",
        examples=["2023-01-20"]
    )
    expiry_date: Optional[date] = Field(
        None,
        description="Date the document expires, in YYYY-MM-DD format",
        examples=["2033-01-19"]
    )
    
    # This creates a graph edge "holder" to a "Person" node.
    holder: Optional[Person] = Field(
        None,
        description="The person this card belongs to"
    )

    def __str__(self):
        return f"{self.document_type} {self.document_number}"

