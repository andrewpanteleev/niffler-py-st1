import time
import pytest
import allure
from playwright.sync_api import Page

from models.spend import SpendAdd
from clients.spends_client import SpendsHttpClient
from marks import Pages, TestData
from datetime import datetime


pytestmark = [
    allure.epic('Database Tests'),
    allure.feature('Spending Operations')
]


TEST_CATEGORY = "School"


@allure.story('DB: Verify spending is added')
@Pages.main_page
def test_spending_should_be_add_db(page: Page, spend_db, envs, spends_client: SpendsHttpClient) -> None:
    # Arrange
    category = spends_client.add_category(TEST_CATEGORY)
    spend = SpendAdd(
        amount=100,
        description=f"Test DB Spend {int(time.time())}",
        category=TEST_CATEGORY,
        spendDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        currency="RUB"
    )

    page.reload()
    # Act
    page.get_by_label("Category *").click()
    page.get_by_text(TEST_CATEGORY).click()
    page.get_by_label("Amount *").fill(str(spend.amount))
    page.get_by_label("Description").fill(spend.description)
    page.get_by_role("button", name="Add new spending").click()

    # Assert
    result = spend_db.get_user_spends(envs.test_username)
    assert any(s.description == spend.description for s in result), "Расход не найден в БД"

    # Cleanup
    spends = spend_db.get_user_spends(envs.test_username)
    spend_id = next(s.id for s in spends if s.description == spend.description)
    spends_client.remove_spends([spend_id])
    spend_db.delete_category(category.id)


@allure.story('DB: Verify spending is deleted')
@Pages.main_page
def test_spending_should_be_deleted_db(page: Page, spend_db, envs, spends_client: SpendsHttpClient):
    # Arrange
    category = spends_client.add_category(TEST_CATEGORY)
    spend = SpendAdd(
        amount=100,
        description=f"Test DB Spend {int(time.time())}",
        category=TEST_CATEGORY,
        spendDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        currency="RUB"
    )

    page.reload()
    # # Act
    page.get_by_label("Category *").click()
    page.get_by_text(TEST_CATEGORY).click()
    page.get_by_label("Amount *").fill(str(spend.amount))
    page.get_by_label("Description").fill(spend.description)
    page.get_by_role("button", name="Add new spending").click()

    time.sleep(1)

    spends = spend_db.get_user_spends(envs.test_username)
    spend_id = next(s.id for s in spends if s.description == spend.description)
    spends_client.remove_spends([spend_id])

    # Assert
    result = spend_db.get_user_spends(envs.test_username)
    assert not any(s.description == spend.description for s in result), "Расход все еще присутствует в БД"

    # Cleanup
    spend_db.delete_category(category.id)