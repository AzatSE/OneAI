from pydantic import BaseModel

class Base(BaseModel):
    model_config = {
        "from_attributes": True
    }

class UserSchema(Base):
    name: str

    class Config:
        from_attributes = True



class UserCreate(Base):
    name: str
    username: str
    password: str


class UserResponse(Base):
    id: int
    name: str
    username: str


"""__________USERS/ME_________"""

class UsersUpdateMe(Base):
    username: str
    email: str

class UpdatePassword(Base):
    current_password: str
    new_password: str

"""_________TASKs_________"""


class TaskCreate(Base):
    task:str

class EditTask(Base):
    task:str

class TaskComlite(Base):
    comlite: bool

class TaskRead(BaseModel):
    id: int
    task: str
    comlite: bool
    user_id: int

    class Config:
        from_attributes = True




"""__________TOKEN_________"""

class Token(Base):
    access_token: str
    token_type: str

class TokenData(Base):
    username: str | None = None
    scopes: list[str] = []

class TokenR(Base):
    refresh_token: str
    token_type: str

class Tokens(Base):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshRequest(Base):
    refresh_token: str
    token_type: str