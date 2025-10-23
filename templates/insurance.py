"""
Pydantic templates for Insurance documents.

This file is self-contained and has no external template dependencies.
It includes all necessary sub-models and provides examples for each field.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Union
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
        examples=[500.00, 150000.00, 75.50]
    )
    currency: Optional[str] = Field(
        None,
        description="The ISO 4217 currency code",
        examples=["EUR", "USD", "CAD"]
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
        examples=["1 Rue de Rivoli", "221B Baker Street"]
    )
    city: Optional[str] = Field(
        None,
        description="City",
        examples=["Paris", "London"]
    )
    state_or_province: Optional[str] = Field(
        None,
        description="State, province, or region",
        examples=["Île-de-France", "London"]
    )
    postal_code: Optional[str] = Field(
        None,
        description="Postal or ZIP code",
        examples=["75001", "NW1 6XE"]
    )
    country: Optional[str] = Field(
        None,
        description="Country",
        examples=["France", "United Kingdom"]
    )

    def __str__(self):
        parts = [self.street_address, self.city, self.state_or_province, self.postal_code, self.country]
        return ", ".join(p for p in parts if p)

# --- Reusable Entity: Organization ---
class Organization(BaseModel):
    """
    A generic model for any organization (insurer, etc.).
    Its name is its unique identifier in the graph.
    """
    model_config = ConfigDict(graph_id_fields=['name'])
    
    name: str = Field(
        ...,
        description="The legal name of the organization",
        examples=["AXA Assurance", "Allianz", "MAIF"]
    )
    phone: Optional[str] = Field(
        None,
        description="Contact phone number",
        examples=["+33 1 40 75 57 00"]
    )
    email: Optional[str] = Field(
        None,
        description="Contact email address",
        examples=["service.client@axa.fr"]
    )
    website: Optional[str] = Field(
        None,
        description="Official website",
        examples=["www.axa.fr"]
    )
    tax_id: Optional[str] = Field(
        None,
        description="Tax ID, VAT ID, or other official identifier"
    )
    
    addresses: List[Address] = Field(
        default_factory=list,
        description="List of physical addresses for the organization"
    )
    
    def __str__(self):
        return self.name

# --- Reusable Entity: Person ---
class Person(BaseModel):
    """
    A generic model for a person (policyholder, etc.).
    A person is uniquely identified by their full name and date of birth.
    """
    model_config = ConfigDict(graph_id_fields=['first_name', 'last_name', 'date_of_birth'])
    
    first_name: Optional[str] = Field(
        None,
        description="The person's given name(s)",
        examples=["Jean", "Sophie"]
    )
    last_name: Optional[str] = Field(
        None,
        description="The person's family name (surname)",
        examples=["Valjean", "Neveu"]
    )
    date_of_birth: Optional[date] = Field(
        None,
        description="Date of birth in YYYY-MM-DD format",
        examples=["1985-03-12"]
    )
    place_of_birth: Optional[str] = Field(
        None,
        description="City and/or country of birth"
    )
    gender: Optional[str] = Field(
        None,
        description="Gender or sex of the person",
        examples=["M", "F"]
    )
    nationality: Optional[str] = Field(
        None,
        description="Nationality of the person",
        examples=["Française"]
    )
    phone: Optional[str] = Field(
        None,
        description="Contact phone number",
        examples=["+33 7 98 76 54 32"]
    )
    email: Optional[str] = Field(
        None,
        description="Contact email address",
        examples=["jean.valjean@email.com"]
    )
    
    addresses: List[Address] = Field(
        default_factory=list,
        description="List of physical addresses (e.g., home, work)"
    )
    
    def __str__(self):
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p)

# --- Document-Specific Entity: Guarantee ---
class Guarantee(BaseModel):
    """
    A single guarantee or coverage item.
    Uniquely identified by its name within the policy.
    """
    model_config = ConfigDict(graph_id_fields=['name'])
    
    name: str = Field(
        ...,
        description="Name of the coverage",
        examples=["Dégât des eaux", "Vol et vandalisme", "Responsabilité civile", "Incendie"]
    )
    description: Optional[str] = Field(
        None,
        description="A brief description of what the guarantee covers",
        examples=["Couvre les dommages causés par les fuites d'eau, ruptures de canalisation.", "Indemnisation en cas de vol par effraction ou de dégradation."]
    )
    coverage_limit: Optional[MonetaryAmount] = Field(
        None,
        description="The maximum amount covered for this guarantee"
    )
    deductible: Optional[MonetaryAmount] = Field(
        None,
        description="The amount the policyholder must pay out-of-pocket (franchise)"
    )
    
    def __str__(self):
        return self.name

# --- Document-Specific Entity: InsurancePlan ---
class InsurancePlan(BaseModel):
    """
    A specific plan or option (e.g., "Basic", "Premium").
    Uniquely identified by its name.
    """
    model_config = ConfigDict(graph_id_fields=['name'])
    
    name: str = Field(
        ...,
        description="The name of the insurance plan or formula",
        examples=["Formule Essentielle", "Formule Confort", "Formule Intégrale"]
    )
    price: Optional[MonetaryAmount] = Field(
        None,
        description="The price for this specific plan"
    )
    
    # Creates edges to all Guarantee nodes included in this plan
    guarantees: List[Guarantee] = Field(
        default_factory=list,
        description="List of guarantees included in this plan"
    )
    
    def __str__(self):
        return self.name

# --- Root Document Model: InsurancePolicy ---
class InsurancePolicy(BaseModel):
    """
    The root model for a generic insurance policy document.
    Identified by its policy number.
    """
    model_config = ConfigDict(graph_id_fields=['policy_number'])
    
    policy_number: str = Field(
        ...,
        description="The unique identifier for this insurance policy contract",
        examples=["A12B3456789", "987654321-C"]
    )
    policy_type: Optional[str] = Field(
        None,
        description="The type of insurance (e.g., Home, Auto, Health)",
        examples=["Assurance Habitation", "Assurance Auto", "Mutuelle Santé"]
    )
    effective_date: Optional[date] = Field(
        None,
        description="The date the policy coverage starts (YYYY-MM-DD)",
        examples=["2024-01-01"]
    )
    expiry_date: Optional[date] = Field(
        None,
        description="The date the policy coverage ends (YYYY-MM-DD)",
        examples=["2025-01-01"]
    )
    
    # The insurer is an Organization
    insurer: Optional[Organization] = Field(
        None,
        description="The insurance company providing the policy"
    )
    
    # The policyholder can be either a Person or an Organization.
    policy_holder: Optional[Union[Person, Organization]] = Field(
        None,
        description="The individual or entity covered by the policy"
    )
    
    # List of insured items (e.g., properties, vehicles)
    insured_assets: List[str] = Field(
        default_factory=list,
        description="A list of assets covered by this policy, described as text",
        examples=[
            "Appartement 5 pièces 123 Rue de la Paix, 75001 Paris",
            "Véhicule Renault Clio immatriculé AB-123-CD",
            "Maison 150m2 au 10 Rue du Chêne, 33000 Bordeaux"
        ]
    )
    
    # Creates edges to the plan(s) included in this policy
    plans: List[InsurancePlan] = Field(
        default_factory=list,
        description="The plan(s) selected for this policy"
    )
    
    total_premium: Optional[MonetaryAmount] = Field(
        None,
        description="The total premium for the policy (e.g., annually or monthly)"
    )

    def __str__(self):
        return f"Policy {self.policy_number}"

