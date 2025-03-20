import os
import pytest
from dotenv import load_dotenv
from faker import Faker
from playwright.sync_api import sync_playwright, Page
from clients.spends_client import SpendsHttpClient
from tests.pages.login_page import LoginPage
from databases.spend_db import SpendDb
from models.config import Envs


@pytest.fixture(scope="session")
def envs() -> Envs:
    load_dotenv()
    return Envs(
        frontend_url=os.getenv("FRONTEND_URL"),
        gateway_url=os.getenv("GATEWAY_URL"),
        spend_db_url=os.getenv("SPENDS_DB_URL"),
        test_username=os.getenv("TEST_USERNAME"),
        test_password=os.getenv("TEST_PASSWORD"),
        invalid_user=os.getenv("INVALID_USER"),
        invalid_password=os.getenv("INVALID_PASSWORD"),
        wrong_password=os.getenv("WRONG_PASSWORD")
    )


@pytest.fixture
def generate_test_user():
    fake = Faker()
    return fake.user_name()


@pytest.fixture(scope="function")
def playwright_context():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def page(playwright_context, envs):
    page = playwright_context.new_page()
    page.goto(envs.frontend_url)
    yield page
    page.close()


@pytest.fixture(scope="function")
def auth(page: Page, envs) -> str:
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in(envs)
    page.wait_for_url("**/main")

    return page.evaluate("window.sessionStorage.getItem('id_token')")


@pytest.fixture(scope="function")
def spends_client(envs, auth) -> SpendsHttpClient:
    return SpendsHttpClient(envs.gateway_url, auth)


@pytest.fixture(scope="session")
def spend_db(envs) -> SpendDb:
    return SpendDb(envs.spend_db_url)


@pytest.fixture(params=[])
def category(request, spends_client, spend_db):
    category_name = request.param
    category = spends_client.add_category(category_name)
    yield category.category
    spend_db.delete_category(category.id)


@pytest.fixture(params=[])
def spends(request, spends_client):
    test_spend = spends_client.add_spends(request.param)
    yield test_spend
    all_spends = spends_client.get_spends()
    if test_spend.id in [spend.id for spend in all_spends]:
        spends_client.remove_spends([test_spend.id])


@pytest.fixture(scope="function")
def main_page(auth, page: Page):
    return page
