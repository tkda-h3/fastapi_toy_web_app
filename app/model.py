from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    access_token: str
    refresh_token: str
    expires_at: int
    scope: str