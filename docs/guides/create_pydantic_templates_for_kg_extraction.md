# **Complete Guide to Creating Pydantic Templates for Knowledge Graph Extraction**

This comprehensive guide provides domain-agnostic best practices for creating Pydantic templates optimized for LLM-based document extraction and automatic conversion to knowledge graphs. The patterns and practices described here are derived from production templates across multiple domains and ensure consistency in structure, validation, and graph representation.

## **Table of Contents**

1. [Core Concepts](#1-core-concepts)
2. [Required Imports and Helper Functions](#2-required-imports-and-helper-functions)
3. [Template Structure and Organization](#3-template-structure-and-organization)
4. [Entity vs Component Classification](#4-entity-vs-component-classification)
5. [Field Definition Patterns](#5-field-definition-patterns)
6. [Validation and Normalization](#6-validation-and-normalization)
7. [Edge Definitions and Relationships](#7-edge-definitions-and-relationships)
8. [Advanced Patterns](#8-advanced-patterns)
9. [String Representations](#9-string-representations)
10. [Common Reusable Components](#10-common-reusable-components)



## **1. Core Concepts**

### **Why Pydantic for Knowledge Graph Extraction?**

Pydantic models serve three critical purposes in the extraction pipeline:

1. **LLM Guidance**: Field descriptions and examples guide the language model to extract accurate, structured data
2. **Data Validation**: Field validators ensure data quality and consistency
3. **Graph Structure**: Models define nodes, edges, and relationships for the knowledge graph

### **Key Terminology**

| Term | Definition | Graph Behavior |
|:-----|:-----------|:---------------|
| **Entity** | A unique, identifiable object tracked individually | Identified by `graph_id_fields` |
| **Component** | A value object deduplicated by content | Set `is_entity=False` |
| **Node** | Any Pydantic model that becomes a graph node | All BaseModel subclasses |
| **Edge** | A relationship between nodes | Defined via `edge()` helper |
| **graph_id_fields** | Fields used to create stable, unique node IDs | Required for entities |



## **2. Required Imports and Helper Functions**

### **Standard Import Block**

Every template must include this import structure:

```python
"""
Brief description of what this template extracts.
Mention the document type and key domain features.
"""

from typing import Any, List, Optional, Union, Self, Type
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from datetime import date, datetime  # Include based on domain needs
from enum import Enum  # Include if using enums
import re  # Include if using regex validators
```

### **Edge Helper Function** (Required)

This function **must be defined identically** in every template:

```python
def edge(label: str, **kwargs: Any) -> Any:
    """
    Helper function to create a Pydantic Field with edge metadata.
    The 'edge_label' defines the type of relationship in the knowledge graph.
    """
    return Field(..., json_schema_extra={"edge_label": label}, **kwargs)
```

**Critical Rules:**
- Function name must be lowercase `edge` (not `Edge`)
- Returns `Field(...)` with `json_schema_extra={"edge_label": label}`
- Always accepts `**kwargs` to pass through additional Field parameters



## **3. Template Structure and Organization**

### **Standard File Organization**

Organize your template in this exact order:

```python
"""
Template docstring describing purpose and domain
"""

# --- Required Imports ---
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Any, List, Optional
# ... additional imports

# --- Edge Helper Function ---
def edge(label: str, **kwargs: Any) -> Any:
    return Field(..., json_schema_extra={"edge_label": label}, **kwargs)

# --- Helper Functions (if needed) ---
# Normalization, parsing, or utility functions

# --- Reusable Components ---
# Value objects with is_entity=False

# --- Reusable Entities ---
# Common entities like Person, Organization, Address

# --- Domain-Specific Models ---
# Models unique to this document type

# --- Root Document Model ---
# The main entry point (last in file)
```

### **Docstring Standards**

Each model should have a clear docstring:

```python
class MyModel(BaseModel):
    """
    Brief description of what this model represents.
    Include uniqueness criteria if it's an entity.
    """
```



## **4. Entity vs Component Classification**

### **The Critical Distinction**

| Aspect | Entity | Component |
|:-------|:-------|:----------|
| **Purpose** | Unique, identifiable objects | Value objects, content-based deduplication |
| **Configuration** | `graph_id_fields=[...]` | `is_entity=False` |
| **Deduplication** | By specified ID fields | By all field values |
| **When to Use** | Track individually (people, documents, organizations) | Shared values (addresses, amounts, measurements) |

### **Entity Pattern**

```python
class Person(BaseModel):
    """
    A person entity.
    Uniquely identified by first name, last name, and date of birth.
    """
    model_config = ConfigDict(graph_id_fields=["first_name", "last_name", "date_of_birth"])
    
    first_name: Optional[str] = Field(...)
    last_name: Optional[str] = Field(...)
    date_of_birth: Optional[date] = Field(...)
    # Additional fields...
```

### **Component Pattern**

```python
class Address(BaseModel):
    """
    A physical address component.
    Deduplicated by content - identical addresses share the same node.
    """
    model_config = ConfigDict(is_entity=False)
    
    street_address: Optional[str] = Field(...)
    city: Optional[str] = Field(...)
    postal_code: Optional[str] = Field(...)
    country: Optional[str] = Field(...)
```

### **Choosing graph_id_fields**

Select fields that:
- Together form a natural unique identifier
- Are stable (don't change frequently)
- Are likely to be present in the extracted data

**Examples:**
- `["document_number"]` - for documents with unique IDs
- `["name"]` - for organizations (if names are unique)
- `["first_name", "last_name", "date_of_birth"]` - for people
- `["name", "text_value", "numeric_value", "unit"]` - for measurements



## **5. Field Definition Patterns**

### **Field Anatomy**

```python
field_name: FieldType = Field(
    default_value,  # ... for required, None for optional, or a default
    description="Detailed, LLM-friendly description with extraction hints",
    examples=["Example 1", "Example 2", "Example 3"]  # 2-5 realistic examples
)
```

### **Required vs Optional Fields**

```python
# Required field - LLM must extract this
document_id: str = Field(
    ...,  # Ellipsis = required
    description="Unique document identifier",
    examples=["DOC-2024-001", "INV-123456"]
)

# Optional field with None default
phone: Optional[str] = Field(
    None,
    description="Contact phone number",
    examples=["+33 1 23 45 67 89", "06 12 34 56 78"]
)

# Optional field with custom default
status: str = Field(
    "pending",
    description="Current processing status",
    examples=["pending", "approved", "rejected"]
)

# Optional list (always use default_factory)
items: List[Item] = Field(
    default_factory=list,
    description="List of items",
    examples=[[{"name": "Item1"}, {"name": "Item2"}]]
)
```

### **Description Best Practices**

**Good descriptions are:**
- Clear and specific about what to extract
- Include extraction hints (field names, patterns, synonyms)
- Provide parsing or normalization instructions
- Guide the LLM on ambiguous cases

```python
# EXCELLENT - Comprehensive guidance
date_of_birth: Optional[date] = Field(
    None,
    description=(
        "The person's date of birth. "
        "Look for text like 'Date of birth', 'Date de naiss.', or 'Born on'. "
        "Parse formats like 'DD MM YYYY' or 'DDMMYYYY' and normalize to YYYY-MM-DD."
    ),
    examples=["1990-05-15", "1985-12-20", "1978-03-30"]
)

# POOR - Too vague
date_of_birth: Optional[date] = Field(None, description="Birth date")
```

### **Examples Best Practices**

Provide **2-5 diverse, realistic examples** per field:

```python
# For simple fields
email: Optional[str] = Field(
    None,
    description="Contact email address",
    examples=[
        "jean.dupont@email.com",
        "contact@company.fr",
        "info@organization.org"
    ]
)

# For lists - show the list structure
guarantees: List[str] = Field(
    default_factory=list,
    description="List of coverage items",
    examples=[
        ["Fire protection", "Water damage", "Theft"],
        ["Basic coverage", "Extended warranty"],
        ["Liability", "Property damage"]
    ]
)

# For complex nested objects
components: List[Component] = Field(
    default_factory=list,
    description="List of components with roles and amounts",
    examples=[
        [
            {
                "material": {"name": "Steel", "grade": "304"},
                "role": "Primary",
                "amount": {"value": 12.0, "unit": "kg"}
            }
        ]
    ]
)
```



## **6. Validation and Normalization**

### **Field Validators**

Use `@field_validator` for data quality checks and transformations:

```python
class MonetaryAmount(BaseModel):
    """Monetary value with validation."""
    model_config = ConfigDict(is_entity=False)
    
    value: float = Field(...)
    currency: Optional[str] = Field(None)
    
    @field_validator("value")
    @classmethod
    def validate_positive(cls, v: Any) -> Any:
        """Ensure value is non-negative."""
        if v < 0:
            raise ValueError("Monetary amount must be non-negative")
        return v
    
    @field_validator("currency")
    @classmethod
    def validate_currency_format(cls, v: Any) -> Any:
        """Ensure currency is 3 uppercase letters (ISO 4217)."""
        if v and not (len(v) == 3 and v.isupper()):
            raise ValueError("Currency must be 3 uppercase letters (ISO 4217)")
        return v
```

### **Pre-validators (mode='before')**

Use `mode='before'` to transform input before type coercion:

```python
@field_validator("email", mode="before")
@classmethod
def normalize_email(cls, v: Any) -> Any:
    """Convert email to lowercase and strip whitespace."""
    if v:
        return v.lower().strip()
    return v

@field_validator("given_names", mode="before")
@classmethod
def ensure_list(cls, v: Any) -> Any:
    """Ensure given_names is always a list."""
    if isinstance(v, str):
        # Handle comma-separated names
        if "," in v:
            return [name.strip() for name in v.split(",")]
        return [v]
    return v
```

### **Model Validators**

Use `@model_validator` for cross-field validation:

```python
class Measurement(BaseModel):
    """Flexible measurement model with single value or range support."""
    model_config = ConfigDict(is_entity=False)
    
    name: str = Field(...)
    numeric_value: Optional[float] = Field(None)
    numeric_value_min: Optional[float] = Field(None)
    numeric_value_max: Optional[float] = Field(None)
    unit: Optional[str] = Field(None)
    
    @model_validator(mode="after")
    def validate_value_consistency(self) -> Self:
        """Ensure value fields are used consistently."""
        has_single = self.numeric_value is not None
        has_min = self.numeric_value_min is not None
        has_max = self.numeric_value_max is not None
        
        # Reject ambiguous cases
        if has_single and has_min and has_max:
            raise ValueError(
                "Cannot specify numeric_value, numeric_value_min, "
                "and numeric_value_max simultaneously"
            )
        
        return self
```

### **Enum Normalization Helper**

For flexible enum handling, use this helper pattern:

```python
from enum import Enum
from typing import Type

def _normalize_enum(enum_cls: Type[Enum], v: Any) -> Any:
    """
    Accept enum instances, value strings, or member names.
    Handles various formats: 'VALUE', 'value', 'Value', 'VALUE_NAME'.
    Falls back to 'OTHER' member if present.
    """
    if isinstance(v, enum_cls):
        return v
    
    if isinstance(v, str):
        # Normalize to alphanumeric lowercase
        key = re.sub(r"[^A-Za-z0-9]+", "", v).lower()
        
        # Build mapping of normalized names/values to enum members
        mapping = {}
        for member in enum_cls:
            normalized_name = re.sub(r"[^A-Za-z0-9]+", "", member.name).lower()
            normalized_value = re.sub(r"[^A-Za-z0-9]+", "", member.value).lower()
            mapping[normalized_name] = member
            mapping[normalized_value] = member
        
        if key in mapping:
            return mapping[key]
        
        # Last attempt: direct value match
        try:
            return enum_cls(v)
        except Exception:
            # Safe fallback to OTHER if present
            if "OTHER" in enum_cls.__members__:
                return enum_cls.OTHER
            raise
    
    raise ValueError(f"Cannot normalize {v} to {enum_cls}")

# Usage in validator
class MyModel(BaseModel):
    status: MyStatusEnum = Field(...)
    
    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: Any) -> Any:
        return _normalize_enum(MyStatusEnum, v)
```



## **7. Edge Definitions and Relationships**

### **Edge() Usage Patterns**

```python
# Required single relationship
issued_by: Organization = edge(
    label="ISSUED_BY",
    description="The organization that issued this document"
)

# Optional single relationship
verified_by: Optional[Person] = edge(
    label="VERIFIED_BY",
    description="Person who verified this document, if applicable"
)

# Required list relationship (one-to-many)
contains_items: List[LineItem] = edge(
    label="CONTAINS_ITEM",
    default_factory=list,  # REQUIRED for lists
    description="Line items contained in this document"
)

# Optional list relationship
addresses: List[Address] = edge(
    label="LOCATED_AT",
    default_factory=list,
    description="Physical addresses for this entity"
)
```

### **Edge Label Conventions**

**Consistent naming standards:**
- Use ALL_CAPS with underscores
- Use verb phrases that describe the relationship
- Choose descriptive, domain-appropriate verbs

**Common edge labels:**
- `ISSUED_BY`, `CREATED_BY`, `OWNED_BY` - authorship/ownership
- `SENT_TO`, `ADDRESSED_TO`, `DELIVERED_TO` - recipients
- `LOCATED_AT`, `LIVES_AT`, `BASED_AT` - physical location
- `CONTAINS_ITEM`, `HAS_COMPONENT`, `INCLUDES_PART` - composition
- `BELONGS_TO`, `PART_OF`, `MEMBER_OF` - membership
- `HAS_GUARANTEE`, `OFFERS_PLAN`, `PROVIDES_COVERAGE` - offerings
- `HAS_PROCESS_STEP`, `HAS_EVALUATION`, `HAS_MEASUREMENT` - processes

**Bad examples (avoid):**
- `issuedBy`, `located-at`, `has guarantee` - inconsistent formatting
- `relationship`, `link`, `connection` - too vague



## **8. Advanced Patterns**

### **Pattern: Flexible Measurement with Range Support**

```python
class Measurement(BaseModel):
    """
    Flexible measurement supporting single values or ranges.
    Can represent '25°C', '1.6 mPa.s', or '80-90°C'.
    """
    model_config = ConfigDict(is_entity=False)
    
    name: str = Field(
        description="Name of the measured property",
        examples=["Temperature", "Viscosity", "pH", "Concentration"]
    )
    
    text_value: Optional[str] = Field(
        default=None,
        description="Textual value if not numerical",
        examples=["High", "Low", "Stable", "Increasing"]
    )
    
    numeric_value: Optional[Union[float, int]] = Field(
        default=None,
        description="Single numerical value",
        examples=[25.0, 1.6, 8.2]
    )
    
    numeric_value_min: Optional[Union[float, int]] = Field(
        default=None,
        description="Minimum value for range measurements",
        examples=[80.0, 1.5]
    )
    
    numeric_value_max: Optional[Union[float, int]] = Field(
        default=None,
        description="Maximum value for range measurements",
        examples=[90.0, 2.0]
    )
    
    unit: Optional[str] = Field(
        default=None,
        description="Unit of measurement",
        examples=["°C", "mPa.s", "wt%", "kg"]
    )
    
    condition: Optional[str] = Field(
        default=None,
        description="Measurement conditions or context",
        examples=["at 25°C", "after 24h", "under normal pressure"]
    )
    
    @model_validator(mode="after")
    def validate_value_consistency(self) -> Self:
        """Ensure value fields don't conflict."""
        has_single = self.numeric_value is not None
        has_min = self.numeric_value_min is not None
        has_max = self.numeric_value_max is not None
        
        if has_single and has_min and has_max:
            raise ValueError(
                "Cannot specify all three: numeric_value, "
                "numeric_value_min, and numeric_value_max"
            )
        
        return self
```

### **Pattern: Nested List with Edges**

```python
class Component(BaseModel):
    """A component with material, role, and amount."""
    model_config = ConfigDict(graph_id_fields=["material", "role"])
    
    material: Material = edge(
        label="USES_MATERIAL",
        description="The material used in this component"
    )
    
    role: RoleEnum = Field(
        description="Function of this component",
        examples=["Primary", "Secondary", "Additive"]
    )
    
    amount: Optional[Measurement] = Field(
        None,
        description="Amount specification"
    )

class Assembly(BaseModel):
    """Root assembly containing components."""
    model_config = ConfigDict(graph_id_fields=["assembly_id"])
    
    assembly_id: str = Field(...)
    
    components: List[Component] = edge(
        label="HAS_COMPONENT",
        default_factory=list,
        description="List of components in this assembly"
    )
```

### **Pattern: Multiple Address Support**

```python
class Entity(BaseModel):
    """Entity that may have multiple addresses."""
    model_config = ConfigDict(graph_id_fields=["name"])
    
    name: str = Field(...)
    
    # Support multiple addresses
    addresses: List[Address] = edge(
        label="LOCATED_AT",
        default_factory=list,
        description="Physical addresses (headquarters, branches, etc.)"
    )
```

### **Pattern: Optional Edges**

```python
class Document(BaseModel):
    """Document that may or may not have a verifier."""
    model_config = ConfigDict(graph_id_fields=["document_id"])
    
    document_id: str = Field(...)
    
    # Optional single edge
    verified_by: Optional[Person] = edge(
        label="VERIFIED_BY",
        description="Person who verified this document, if verified"
    )
```

### **Pattern: Conditional Fields with Validators**

```python
class Document(BaseModel):
    """Document with type-specific fields."""
    
    document_type: str = Field(
        description="Type of document",
        examples=["Invoice", "Receipt", "Credit Note"]
    )
    
    # Field only relevant for invoices
    payment_terms: Optional[str] = Field(
        None,
        description="Payment terms (primarily for invoices)",
        examples=["Net 30", "Due on receipt", "Net 60"]
    )
    
    # Field only relevant for credit notes
    original_document_ref: Optional[str] = Field(
        None,
        description="Reference to original document (for credit notes)",
        examples=["INV-2024-001", "DOC-123456"]
    )
```



## **9. String Representations**

### **Purpose and Placement**

Add `__str__` methods to all entities and key components for:
- Debugging and logging
- Human-readable representation in error messages
- Graph visualization labels

### **Implementation Patterns**

```python
# Simple concatenation
class Person(BaseModel):
    first_name: Optional[str] = Field(...)
    last_name: Optional[str] = Field(...)
    
    def __str__(self) -> str:
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p) or "Unknown"

# With list handling
class Person(BaseModel):
    given_names: Optional[List[str]] = Field(...)
    last_name: Optional[str] = Field(...)
    
    def __str__(self) -> str:
        first_names = " ".join(self.given_names) if self.given_names else ""
        parts = [first_names, self.last_name]
        return " ".join(p for p in parts if p) or "Unknown"

# Address formatting
class Address(BaseModel):
    street_address: Optional[str] = Field(...)
    city: Optional[str] = Field(...)
    postal_code: Optional[str] = Field(...)
    country: Optional[str] = Field(...)
    
    def __str__(self) -> str:
        parts = [
            self.street_address,
            self.city,
            self.postal_code,
            self.country
        ]
        return ", ".join(p for p in parts if p)

# Value with unit
class MonetaryAmount(BaseModel):
    value: float = Field(...)
    currency: Optional[str] = Field(None)
    
    def __str__(self) -> str:
        return f"{self.value} {self.currency or ''}".strip()

# With identifier
class Document(BaseModel):
    document_type: str = Field(...)
    document_number: str = Field(...)
    
    def __str__(self) -> str:
        return f"{self.document_type} {self.document_number}"
```



## **10. Common Reusable Components**

### **Address Component**

```python
class Address(BaseModel):
    """Physical address component (deduplicated by content)."""
    model_config = ConfigDict(is_entity=False)
    
    street_address: Optional[str] = Field(
        None,
        description="Street name and number",
        examples=["123 Main Street", "45 Avenue des Champs-Élysées"]
    )
    
    city: Optional[str] = Field(
        None,
        description="City name",
        examples=["Paris", "London", "New York"]
    )
    
    state_or_province: Optional[str] = Field(
        None,
        description="State, province, or region",
        examples=["Île-de-France", "California", "Ontario"]
    )
    
    postal_code: Optional[str] = Field(
        None,
        description="Postal or ZIP code",
        examples=["75001", "SW1A 1AA", "10001"]
    )
    
    country: Optional[str] = Field(
        None,
        description="Country name or code",
        examples=["France", "FR", "United Kingdom"]
    )
    
    def __str__(self) -> str:
        parts = [
            self.street_address,
            self.city,
            self.state_or_province,
            self.postal_code,
            self.country
        ]
        return ", ".join(p for p in parts if p)
```

### **Monetary Amount Component**

```python
class MonetaryAmount(BaseModel):
    """Monetary value with currency (deduplicated by content)."""
    model_config = ConfigDict(is_entity=False)
    
    value: float = Field(
        ...,
        description="Numeric amount",
        examples=[500.00, 1250.50, 89.99]
    )
    
    currency: Optional[str] = Field(
        None,
        description="ISO 4217 currency code",
        examples=["EUR", "USD", "GBP", "CHF"]
    )
    
    @field_validator("value")
    @classmethod
    def validate_positive(cls, v: Any) -> Any:
        """Ensure amount is non-negative."""
        if v < 0:
            raise ValueError("Monetary amount must be non-negative")
        return v
    
    @field_validator("currency")
    @classmethod
    def validate_currency_format(cls, v: Any) -> Any:
        """Ensure currency is 3 uppercase letters."""
        if v and not (len(v) == 3 and v.isupper()):
            raise ValueError("Currency must be 3 uppercase letters (ISO 4217)")
        return v
    
    def __str__(self) -> str:
        return f"{self.value} {self.currency or ''}".strip()
```

### **Person Entity**

```python
class Person(BaseModel):
    """Person entity (unique by name and date of birth)."""
    model_config = ConfigDict(
        graph_id_fields=["first_name", "last_name", "date_of_birth"]
    )
    
    first_name: Optional[str] = Field(
        None,
        description="Person's given name(s)",
        examples=["Jean", "Maria", "John"]
    )
    
    last_name: Optional[str] = Field(
        None,
        description="Person's family name (surname)",
        examples=["Dupont", "Garcia", "Smith"]
    )
    
    date_of_birth: Optional[date] = Field(
        None,
        description="Date of birth in YYYY-MM-DD format",
        examples=["1985-03-12", "1990-06-20"]
    )
    
    email: Optional[str] = Field(
        None,
        description="Contact email address",
        examples=["jean.dupont@email.com", "maria.garcia@company.com"]
    )
    
    phone: Optional[str] = Field(
        None,
        description="Contact phone number",
        examples=["+33 1 23 45 67 89", "+1 555-123-4567"]
    )
    
    # Edge to Address
    addresses: List[Address] = edge(
        label="LIVES_AT",
        default_factory=list,
        description="Residential addresses"
    )
    
    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: Any) -> Any:
        """Convert email to lowercase and strip whitespace."""
        if v:
            return v.lower().strip()
        return v
    
    def __str__(self) -> str:
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p) or "Unknown"
```

### **Organization Entity**

```python
class Organization(BaseModel):
    """Organization entity (unique by name)."""
    model_config = ConfigDict(graph_id_fields=["name"])
    
    name: str = Field(
        ...,
        description="Legal name of the organization",
        examples=["Acme Corporation", "Tech Solutions Ltd", "Global Industries"]
    )
    
    tax_id: Optional[str] = Field(
        None,
        description="Tax ID, VAT number, or registration number",
        examples=["123456789", "FR12345678901", "GB123456789"]
    )
    
    email: Optional[str] = Field(
        None,
        description="Contact email address",
        examples=["contact@acme.com", "info@techsolutions.com"]
    )
    
    phone: Optional[str] = Field(
        None,
        description="Contact phone number",
        examples=["+33 1 23 45 67 89", "+1 555-987-6543"]
    )
    
    website: Optional[str] = Field(
        None,
        description="Official website URL",
        examples=["www.acme.com", "techsolutions.com"]
    )
    
    # Edge to Address
    addresses: List[Address] = edge(
        label="LOCATED_AT",
        default_factory=list,
        description="Physical addresses (headquarters, branches, etc.)"
    )
    
    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: Any) -> Any:
        """Convert email to lowercase and strip whitespace."""
        if v:
            return v.lower().strip()
        return v
    
    def __str__(self) -> str:
        return self.name
```



## **Checklist for Creating New Templates**

When creating a new template, verify:

- [ ] **Imports**: All necessary imports included
- [ ] **Edge Helper**: `edge()` function defined correctly
- [ ] **File Organization**: Components → Entities → Domain Models → Root
- [ ] **Entity Configuration**: All entities have `graph_id_fields`
- [ ] **Component Configuration**: All components have `is_entity=False`
- [ ] **Field Descriptions**: Clear, detailed, LLM-friendly
- [ ] **Examples**: 2-5 realistic examples per field
- [ ] **Validators**: Data quality checks where needed
- [ ] **Edge Labels**: Descriptive, ALL_CAPS_WITH_UNDERSCORES
- [ ] **List Edges**: All use `default_factory=list`
- [ ] **String Methods**: `__str__` defined for entities
- [ ] **Docstrings**: All models have clear docstrings
- [ ] **Type Hints**: Proper use of Optional, List, Union
- [ ] **Consistency**: Patterns match across similar fields



## **Testing Your Template**

Create a simple test to verify your template works:

```python
# test_my_template.py
from my_template import RootDocument, Entity, Component
from datetime import date

# Create test instance
test_doc = RootDocument(
    document_id="TEST-001",
    issued_by=Entity(
        name="Test Organization",
        addresses=[
            Component(
                street_address="123 Test St",
                city="Paris",
                postal_code="75001",
                country="France"
            )
        ]
    )
)

# Verify it works
print(test_doc)
print(test_doc.model_dump_json(indent=2))
```

***

This guide ensures consistency across all Pydantic templates regardless of domain, enabling reliable LLM extraction and seamless knowledge graph conversion.