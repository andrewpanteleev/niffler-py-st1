from pydantic import BaseModel


class Envs(BaseModel):
    frontend_url: str
    gateway_url: str
    spend_db_url: str
    test_username: str
    test_password: str
    invalid_user: str
    invalid_password: str
    wrong_password: str