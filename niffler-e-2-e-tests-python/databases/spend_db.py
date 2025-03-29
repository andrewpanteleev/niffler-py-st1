from typing import Sequence

import allure
from allure import step
from allure_commons.types import AttachmentType
from sqlalchemy import create_engine, Engine, event
from sqlmodel import Session, select

from models.spend import Spend
from models.config import Envs
from models.category import Category
from utils.allure_helpers import attach_sql


class SpendDb:

    engine: Engine

    def __init__(self, envs: Envs):
        self.engine = create_engine(envs.spend_db_url)
        event.listen(self.engine, "do_execute", fn=attach_sql)

    @step('DB: Get user categories')
    def get_user_categories(self, username: str) -> Sequence[Category]:
        with Session(self.engine) as session:
            statement = select(Category).where(Category.username == username)
            return session.exec(statement).all()

    @step('DB: Delete a category')
    def delete_category(self, category_id: str):
        with Session(self.engine) as session:
            category = session.get(Category, category_id)
            session.delete(category)
            session.commit()

    @step('DB: Retrieve user spends')
    def get_user_spends(self, username: str) -> Sequence[Spend]:
        with Session(self.engine) as session:
            statement = select(Spend).where(Spend.username == username)
            return session.exec(statement).all()