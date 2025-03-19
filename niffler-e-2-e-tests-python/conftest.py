import os
import pytest
from dotenv import load_dotenv
from faker import Faker
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from clients.spends_client import SpendsHttpClient
from tests.pages.login_page import LoginPage
from typing import Dict, Tuple, Any, List, Optional, Generator, Callable


@pytest.fixture(scope="session")
def envs() -> None:
    load_dotenv()


@pytest.fixture(scope="session")
def frontend_url(envs) -> str:
    return os.getenv("FRONTEND_URL")


@pytest.fixture(scope="session")
def gateway_url(envs) -> str:
    return os.getenv("GATEWAY_URL")


@pytest.fixture(scope="session")
def app_user(envs) -> Tuple[str, str]:
    return os.getenv("TEST_USERNAME"), os.getenv("TEST_PASSWORD")


@pytest.fixture
def generate_test_user() -> str:
    fake = Faker()
    return fake.user_name()


@pytest.fixture(scope="function")
def playwright_context() -> Generator[BrowserContext, None, None]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def page(playwright_context: BrowserContext, frontend_url: str) -> Generator[Page, None, None]:
    page = playwright_context.new_page()
    page.goto(frontend_url)
    yield page
    page.close()


@pytest.fixture(scope="function")
def auth(page: Page, app_user: Tuple[str, str]) -> str:
    username, password = app_user
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in(username, password)
    page.wait_for_url("**/main")

    return page.evaluate("window.sessionStorage.getItem('id_token')")


@pytest.fixture(scope="function")
def spends_client(gateway_url: str, auth: str) -> SpendsHttpClient:
    client = SpendsHttpClient(gateway_url, auth)
    return client


@pytest.fixture(params=[])
def category(request: pytest.FixtureRequest, spends_client: SpendsHttpClient) -> str:
    category_name = request.param
    current_categories = spends_client.get_categories()
    category_names = [category["category"] for category in current_categories]
    if category_name not in category_names:
        spends_client.add_category(category_name)
    return category_name


@pytest.fixture(params=[])
def spends(request: pytest.FixtureRequest, spends_client: SpendsHttpClient) -> Dict[str, Any]:
    spend = spends_client.add_spends(request.param)
    yield spend

    try:
        all_spends = spends_client.get_spends()
        spend_exists = any(s["id"] == spend["id"] for s in all_spends)

        if spend_exists:
            spends_client.remove_spends([spend["id"]])
    except Exception as e:
        print(f"Ошибка при удалении расхода {spend['id']}: {e}")


@pytest.fixture(scope="function")
def main_page(auth: str, page: Page) -> Page:
    return page
