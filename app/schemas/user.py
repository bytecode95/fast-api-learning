# We separate create, update, read, and list schemas so the API contract doesn't expose database implementation details.
from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr


class UserUpdate(BaseModel):
    # All fields are optional for PATCH.
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    is_active: bool | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    items: list[UserRead]
    total: int
    limit: int
    offset: int


"""
Why separate schemas?
- UserCreate: clients cannot set their own ID or timestamps.
- UserUpdate: only supplied fields are updated.
- UserRead: only explicitly approved fields are returned.
- UserListResponse: provides a consistent pagination contract.
EmailStr validates email syntax. It does not verify that an address belongs to a real person.


"""
