from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


@dataclass
class User:
    id: UUID
    email: str
    hashed_password: str
    role: UserRole
    created_at: datetime
    is_active: bool = True
    
    @classmethod
    def create(cls, email: str, hashed_password: str, role: UserRole = UserRole.BUYER) -> "User":
        return cls(
            id=uuid4(),
            email=email.lower(),
            hashed_password=hashed_password,
            role=role,
            created_at=datetime.now(timezone.utc),
        )
    
    def deactivate(self) -> None:
        self.is_active = False
    
    def activate(self) -> None:
        self.is_active = True
    
    def change_email(self, new_email: str) -> None:
        self.email = new_email.lower()