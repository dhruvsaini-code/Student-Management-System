from dataclasses import dataclass

@dataclass
class Admin:
    """Represents an admin login credential.

    Attributes:
        username: Unique admin username.
        password_hash: bcrypt hashed password string.
        created_at: ISO date-time string when this user was registered.
    """
    username: str
    password_hash: str
    created_at: str
