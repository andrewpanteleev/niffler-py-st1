import os
from dotenv import load_dotenv
import pytest
from playwright.sync_api import sync_playwright
from faker import Faker


load_dotenv()


@pytest.fixture(scope="session")
def app_url():
    return os.getenv("APP_URL")

@pytest.fixture(scope="session")
def app_auth_url():
    return os.getenv("APP_AUTH_URL")

@pytest.fixture(scope="session")
def credentials():
    user = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    return {"user": user, "password": password}

@pytest.fixture(scope="function")
def playwright_context():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        yield context
        context.close()
        browser.close()

@pytest.fixture(scope="function")
def page(playwright_context, app_url):
    page = playwright_context.new_page()
    page.goto(app_url)
    yield page
    page.close()

@pytest.fixture
def generate_test_user():
    fake = Faker()
    return fake.user_name()
