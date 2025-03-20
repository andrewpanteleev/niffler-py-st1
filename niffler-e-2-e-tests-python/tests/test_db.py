import time
import pytest
from playwright.sync_api import Page
from models.spend import SpendAdd
from clients.spends_client import SpendsHttpClient
from marks import Pages, TestData
from datetime import datetime


TEST_CATEGORY = "School"


# 1. Тест проверки, что при добавлении расхода, расход сохраняется в БД
@Pages.main_page
@TestData.category(TEST_CATEGORY)
@TestData.spends(
    SpendAdd(
        amount=100,
        description=f"Test DB Spend {int(time.time())}",
        category=TEST_CATEGORY,
        spendDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        currency="RUB"
    )
)
def test_spending_should_be_add_db(page: Page, category: str, spends, spend_db, envs) -> None:
    result = spend_db.get_user_spends(envs.test_username)

    assert any(spend.description == spends.description for spend in result), "Расход не найден в БД"


# 2. Тест проверки, что при удалении расхода, расход удаляется из БД
@Pages.main_page
@TestData.category(TEST_CATEGORY)
@TestData.spends(
    SpendAdd(
        amount=100,
        description=f"Test DB Spend {int(time.time())}",
        category=TEST_CATEGORY,
        spendDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        currency="RUB"
    )
)
def test_spending_should_be_deleted_db(page: Page, category: str, spends, spend_db, spends_client: SpendsHttpClient, envs):
    spends_client.remove_spends([spends.id])
    result = spend_db.get_user_spends(envs.test_username)

    assert not result