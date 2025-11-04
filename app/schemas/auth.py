from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username_or_email: str = Field(json_schema_extra={"example": "jane@example.com"})
    password: str = Field(json_schema_extra={"example": "StrongPassword123!"})


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


