import pytest
from playwright.sync_api import sync_playwright, Page
from playwright.sync_api import expect


@pytest.fixture(scope="function")
def playwright_context():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
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
def main_page(auth_token, page: Page, envs):
    page.evaluate("""token => {
        sessionStorage.setItem('id_token', token);
    }""", auth_token)

    page.goto(envs.frontend_url)
        
    return page