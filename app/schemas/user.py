import re
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    validator,
    root_validator,
    SecretStr,
    constr,
)
from typing import Optional


class User(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    msg: str = Field(default="User created Successfully")


class CreateUserReq(BaseModel):
    email: EmailStr
    password: SecretStr = Field(min_length=8, max_length=20)
    name: str = Field(max_length=20, min_length=3, pattern=r"^[a-zA-Z\s]+$")
    bio: Optional[str] = Field(max_length=50)

    @validator("password")
    def password_must_match_pattern(cls, val):
        value = val.get_secret_value()
        pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[#?!@$%^&*-]).{8,}$"
        if len(value) < 8:
            raise ValueError("Password must have at least 8 characters")
        if not re.match(pattern, value):
            raise ValueError(
                "Password must have at least one uppercase letter, one lowercase letter, one digit, and one special character"
            )

        return val
