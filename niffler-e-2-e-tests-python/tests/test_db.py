import time
import pytest
import allure
from playwright.sync_api import Page

from models.spend import SpendAdd
from clients.spends_client import SpendsHttpClient
from marks import Pages, TestData
from models.enums import Category
from datetime import datetime


pytestmark = [
    allure.epic('Database Tests'),
    allure.feature('Spending Operations')
]


@allure.story('DB: Verify spending is added')
@Pages.main_page
@TestData.category(Category.SCHOOL)
def test_spending_should_be_add_db(page: Page, category, spend_db, envs, spends_client: SpendsHttpClient) -> None:
    spend = SpendAdd(
        amount=100,
        description=f"Test DB Spend {int(time.time())}",
        category=Category.SCHOOL,
        spendDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        currency="RUB"
    )

    page.reload()

    page.get_by_label("Category *").click()
    page.get_by_text(Category.SCHOOL).click()
    page.get_by_label("Amount *").fill(str(spend.amount))
    page.get_by_label("Description").fill(spend.description)
    page.get_by_role("button", name="Add new spending").click()


    result = spend_db.get_user_spends(envs.test_username)
    assert any(s.description == spend.description for s in result), "Расход не найден в БД"


    spends = spend_db.get_user_spends(envs.test_username)
    spend_id = next(s.id for s in spends if s.description == spend.description)
    spends_client.remove_spends([spend_id])


@allure.story('DB: Verify spending is deleted')
@Pages.main_page
@TestData.category(Category.SCHOOL)
def test_spending_should_be_deleted_db(page: Page, category, spend_db, envs, spends_client: SpendsHttpClient):
    spend = SpendAdd(
        amount=100,
        description=f"Test DB Spend {int(time.time())}",
        category=Category.SCHOOL,
        spendDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        currency="RUB"
    )

    page.reload()

    page.get_by_label("Category *").click()
    page.get_by_text(Category.SCHOOL).click()
    page.get_by_label("Amount *").fill(str(spend.amount))
    page.get_by_label("Description").fill(spend.description)
    page.get_by_role("button", name="Add new spending").click()

    time.sleep(1)

    spends = spend_db.get_user_spends(envs.test_username)
    spend_id = next(s.id for s in spends if s.description == spend.description)
    spends_client.remove_spends([spend_id])


    result = spend_db.get_user_spends(envs.test_username)
    assert not any(s.description == spend.description for s in result), "Расход все еще присутствует в БД"
