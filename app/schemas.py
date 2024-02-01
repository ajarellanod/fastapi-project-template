from pydantic import BaseModel, ConfigDict


# Base model representing minimal shared information between schemas
class ExampleBase(BaseModel):
    """The foundational schema providing basic info"""

    code: str
    value: str


# Specific schema dedicated to serving responses to client requests
class Example(ExampleBase):
    """Customized schema for organized API responses"""

    # This is optional! It is for parse python objects.
    model_config = ConfigDict(from_attributes=True)


# Targeted schema governing input parameters during resource creation
class ExampleCreate(BaseModel):
    """Schema guiding the construction of new resources"""

    code: str


# Focused schema facilitating alterations to established resources
class ExampleUpdate(BaseModel):
    """Schema directing partial updates to existing entries"""

    code: str | None = None
