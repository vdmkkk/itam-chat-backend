from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username_or_email: str = Field(examples=["jane@example.com", "jane_doe"])
    password: str = Field(examples=["StrongPassword123!"])


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


