"""
Database Schemas

Pydantic models that map to MongoDB collections for the Construction Network app.
Each class name becomes the collection name in lowercase.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, AnyUrl


class Profile(BaseModel):
    """
    Professional profiles across the construction and real-estate ecosystem.
    Collection: "profile"
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Primary contact email")
    role: str = Field(..., description="e.g., Contractor, Architect, Interior Designer, Carpenter, Manufacturer, Supplier, Buyer, Realtor")
    company: Optional[str] = Field(None, description="Company or organization")
    location: Optional[str] = Field(None, description="City, State or Region")
    skills: List[str] = Field(default_factory=list, description="Key skills or specialties")
    services: List[str] = Field(default_factory=list, description="Services offered")
    bio: Optional[str] = Field(None, description="Short bio")
    phone: Optional[str] = Field(None, description="Contact phone number")
    website: Optional[AnyUrl] = Field(None, description="Personal or company website")
    avatar_url: Optional[AnyUrl] = Field(None, description="Profile image URL")


class Company(BaseModel):
    """
    Companies and organizations in the ecosystem.
    Collection: "company"
    """
    name: str
    industry: str = Field(..., description="e.g., Materials, Construction, Architecture, Interior, Real Estate")
    location: Optional[str] = None
    size: Optional[str] = Field(None, description="e.g., 1-10, 11-50, 51-200, 200+")
    website: Optional[AnyUrl] = None
    description: Optional[str] = None


class Post(BaseModel):
    """
    Feed posts or updates by professionals.
    Collection: "post"
    """
    author_email: str
    content: str = Field(..., max_length=2000)
    tags: List[str] = Field(default_factory=list)
    images: List[AnyUrl] = Field(default_factory=list)


class Connection(BaseModel):
    """
    Connection requests between two profiles.
    Collection: "connection"
    """
    from_email: str
    to_email: str
    status: str = Field("pending", description="pending | accepted | rejected")


# You can extend with more schemas later (projects, jobs, tenders, reviews, messages)
