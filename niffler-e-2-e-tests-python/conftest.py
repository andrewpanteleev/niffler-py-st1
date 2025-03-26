import os

import allure
import pytest
from allure_commons.reporter import AllureReporter
from allure_commons.types import AttachmentType
from allure_pytest.listener import AllureListener
from pytest import Item, FixtureDef, FixtureRequest
from dotenv import load_dotenv
from faker import Faker
from playwright.sync_api import sync_playwright, Page
from clients.auth_client import AuthClient
from clients.spends_client import SpendsHttpClient
from tests.pages.login_page import LoginPage
from databases.spend_db import SpendDb
from models.config import Envs


def allure_logger(config) -> AllureReporter:
    listener: AllureListener = config.pluginmanager.get_plugin("allure_listener")
    return listener.allure_logger


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_call(item: Item):
    yield
    allure.dynamic.title(" ".join(item.name.split("_")[1:]).title())


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_fixture_setup(fixturedef: FixtureDef, request: FixtureRequest):
    yield
    logger = allure_logger(request.config)
    item = logger.get_last_item()
    scope_letter = fixturedef.scope[0].upper()
    item.name = f"[{scope_letter}] " + " ".join(fixturedef.argname.split("_")).title()


@pytest.fixture(scope="session")
def envs() -> Envs:
    load_dotenv()
    envs_instance = Envs(
        frontend_url=os.getenv("FRONTEND_URL"),
        gateway_url=os.getenv("GATEWAY_URL"),
        auth_url=os.getenv("AUTH_URL"),
        auth_secret=os.getenv("AUTH_SECRET"),
        spend_db_url=os.getenv("SPENDS_DB_URL"),
        test_username=os.getenv("TEST_USERNAME"),
        test_password=os.getenv("TEST_PASSWORD"),
        invalid_user=os.getenv("INVALID_USER"),
        invalid_password=os.getenv("INVALID_PASSWORD"),
        wrong_password=os.getenv("WRONG_PASSWORD")
    )
    allure.attach(envs_instance.model_dump_json(indent=2), name="envs.json", attachment_type=AttachmentType.JSON)
    return envs_instance

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
def auth_front_token(page: Page, envs: Envs):
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in(envs)
    page.wait_for_url("**/main")

    token = page.evaluate('() => window.sessionStorage.getItem("id_token")')
    allure.attach(token, name="token.txt", attachment_type=AttachmentType.TEXT)
    return token


@pytest.fixture(scope="session")
def auth_api_token(envs: Envs):
    token = AuthClient(envs).auth(envs.test_username, envs.test_password)
    allure.attach(token, name="token.txt", attachment_type=AttachmentType.TEXT)
    return token


@pytest.fixture(scope="session")
def spends_client(envs, auth) -> SpendsHttpClient:
    return SpendsHttpClient(envs.gateway_url, auth)


@pytest.fixture(scope="session")
def spend_db(envs) -> SpendDb:
    return SpendDb(envs.spend_db_url)


@pytest.fixture(params=[])
def category(request: FixtureRequest, spends_client, spend_db):
    category_name = request.param
    category = spends_client.add_category(category_name)
    yield category.category
    spend_db.delete_category(category.id)


@pytest.fixture(params=[])
def spends(request: FixtureRequest, spends_client):
    test_spend = spends_client.add_spends(request.param)
    yield test_spend
    all_spends = spends_client.get_spends()
    if test_spend.id in [spend.id for spend in all_spends]:
        spends_client.remove_spends([test_spend.id])


@pytest.fixture(scope="function")
def main_page(auth_front_token, page: Page):
    return page
