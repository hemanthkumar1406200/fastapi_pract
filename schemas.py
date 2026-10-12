from pydantic import BaseModel

class UserCreate(BaseModel):
    Property_code: str
    Bearer: str | None = None
    Key: str
    Endpoint: str | None = None

class HoteltableCreate(BaseModel):
    reservation_id: str
    confirmation_no: str
    first_name: str
    last_name: str
    room_no: str

class TokenCreate(BaseModel):
    token: str