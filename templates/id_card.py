"""
Pydantic schema for extracting information from a French Identity Card.

This schema is designed for graph conversion. It defines distinct nodes for the
cardholder's information and the document's technical details, linking them back
to a central 'FrenchIDCard' node.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any

# A special object to define graph edges, consistent with other templates
def Edge(label: str, **kwargs: Any) -> Any:
    """Helper function to create a Pydantic Field with edge metadata."""
    return Field(..., json_schema_extra={'edge_label': label}, **kwargs)


# --- Node Definitions ---

class Location(BaseModel):
    """
    Represents a geographical location, such as a city of birth.
    This is a distinct node to allow for easier linking in a larger graph.
    """
    city: str = Field(
        description="The city, town, or municipality of birth.",
        examples=["BORDEAUX", "PARIS"]
    )

class HolderInformation(BaseModel):
    """
    Represents the personal information of the cardholder. This will become a 'Person' node in the graph.
    """
    surname: str = Field(
        description="The last name or family name of the cardholder.",
        examples=["CHEVAILLIER", "CRUISE"]
    )
    given_names: List[str] = Field(
        description="A list of the cardholder's first and middle names.",
        examples=[["Gisèle", "Audrey"], ["Thomas"]]
    )
    sex: str = Field(
        description="The legal sex of the cardholder (e.g., 'F' or 'M').",
        examples=["F", "M"]
    )
    date_of_birth: str = Field(
        description="The cardholder's date of birth, typically in DD MM YYYY format.",
        examples=["01 04 1995", "03 07 1962"]
    )
    nationality: str = Field(
        description="The cardholder's nationality, often as a three-letter code.",
        examples=["FRA"]
    )
    alternate_name: Optional[str] = Field(
        default=None,
        description="An alternate or usage name, such as a married name (Nom d'usage).",
        examples=["vve. DUBOIS"]
    )

    # --- Edge Definition ---
    place_of_birth: Location = Edge(label="BORN_IN")

class DocumentDetails(BaseModel):
    """
    Represents the specific metadata and identifiers of the identity document itself. This will become a 'Document' node.
    """
    document_number: str = Field(
        description="The unique alphanumeric identifier for the document.",
        examples=["T7X62TZ79", "X4RTBPFW4"]
    )
    expiry_date: str = Field(
        description="The date the document expires, typically in DD MM YYYY format.",
        examples=["27 01 2031", "11 02 2030"]
    )
    card_access_number: str = Field(
        description="A secondary number or code on the card, possibly for electronic access.",
        examples=["240220", "384213"]
    )

class FrenchIDCard(BaseModel):
    """
    The central node representing the full French National Identity Card document.
    """
    document_type: str = Field(
        description="The official type of the document.",
        examples=["CARTE NATIONALE D'IDENTITÉ / IDENTITY CARD"]
    )
    issuing_country: str = Field(
        description="The country that issued the identity card.",
        examples=["RÉPUBLIQUE FRANÇAISE"]
    )
    country_code: str = Field(
        description="The two-letter country code for the issuing authority.",
        examples=["FR"]
    )

    # --- Edge Definitions ---
    holder_information: HolderInformation = Edge(label="HELD_BY")
    document_details: DocumentDetails = Edge(label="HAS_DETAILS")

