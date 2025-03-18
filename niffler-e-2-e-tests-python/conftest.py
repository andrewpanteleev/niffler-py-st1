import os
import pytest
from dotenv import load_dotenv
from faker import Faker
from playwright.sync_api import sync_playwright, Page
from clients.spends_client import SpendsHttpClient
from tests.pages.login_page import LoginPage


@pytest.fixture(scope="session")
def envs():
    load_dotenv()


@pytest.fixture(scope="session")
def frontend_url(envs):
    return os.getenv("FRONTEND_URL")


@pytest.fixture(scope="session")
def gateway_url(envs):
    return os.getenv("GATEWAY_URL")


@pytest.fixture(scope="session")
def app_user(envs):
    return os.getenv("TEST_USERNAME"), os.getenv("TEST_PASSWORD")


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
def page(playwright_context, frontend_url):
    page = playwright_context.new_page()
    page.goto(frontend_url)
    yield page
    page.close()


@pytest.fixture(scope="function")
def auth(page: Page, app_user) -> str:
    username, password = app_user
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in(username, password)
    page.wait_for_url("**/main")

    return page.evaluate("window.sessionStorage.getItem('id_token')")


@pytest.fixture(scope="function")
def spends_client(gateway_url, auth) -> SpendsHttpClient:
    client = SpendsHttpClient(gateway_url, auth)
    return client


@pytest.fixture(params=[])
def category(request, spends_client):
    category_name = request.param
    current_categories = spends_client.get_categories()
    category_names = [category["category"] for category in current_categories]
    if category_name not in category_names:
        spends_client.add_category(category_name)
    return category_name


@pytest.fixture(params=[])
def spends(request, spends_client):
    spend = spends_client.add_spends(request.param)
    yield spend
    try:
        # TODO вместо исключения проверить список текущих spends
        spends_client.remove_spends([spend["id"]])
    except Exception:
        pass


@pytest.fixture(scope="function")
def main_page(auth, page: Page):
    return page
