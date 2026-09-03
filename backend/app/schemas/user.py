"""
CashCow Command Center
Pydantic v2 schema for the User and auth resources
"""

from pydantic import BaseModel, ConfigDict, Field

from app.models import UserRole

class UserBase(BaseModel):
    username : str = Field(min_length=3, max_length=50)
    first_name : str = Field(min_length=1, max_length=100)
    last_name : str = Field(min_length=1, max_length=100)
    role : UserRole
    branch_id : int | None = None

class UserCreate(UserBase):
    password : str = Field(min_length=8)

class UserUpdate(BaseModel):
    username : str | None = Field(default=None, min_length=3, max_length=50)
    first_name : str | None = Field(default=None, min_length=1, max_length=100)
    last_name : str | None = Field(default=None, min_length=1, max_length=100)
    password : str | None = Field(default=None, min_length=8)
    role : UserRole | None = None
    branch_id : int | None = None
    is_active : bool | None = None

# We are NOT adding the password to the UserRead schema since we 
# do not want to expose the hashed password in our API responses
class UserRead(UserBase):
    id : int
    is_active : bool
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token : str
    token_type : str = "bearer"