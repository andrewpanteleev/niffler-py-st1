import pytest
import allure
import time
from playwright.sync_api import Page, expect
from .pages.login_page import LoginPage
from .pages.registration_page import RegistrationPage
from .pages.spending_page import SpendingPage
from .pages.profile_page import ProfilePage
from marks import Pages, TestData
from models.enums import Category
from datetime import datetime
from clients.spends_client import SpendsHttpClient
from models.spend import SpendAdd

pytestmark = [
    allure.epic('User management'),
    ]


# 1. Тест успешного логина
@allure.story('Successful login')
def test_successful_login(page: Page, envs) -> None:
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in(envs)
    spending = SpendingPage(page)
    spending.check_spending_page_titles()


# 2. Тест логина несуществующего пользователя
@allure.story('Non-existent user login')
def test_non_existent_user_login(page: Page, envs) -> None:
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in_non_existent_user_login(envs)
    login.check_error_message()


# 3. Тест логина с неправильным паролем
@allure.story('Login with wrong password')
def test_login_wrong_password(page: Page, envs) -> None:
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in_wrong_password(envs)
    login.check_error_message()


# 4. Тест успешной регистрации
@allure.story('Successful registration')
def test_successful_registration(page: Page, generate_test_user: str) -> None:
    registration = RegistrationPage(page)
    registration.register_button.click()
    user = generate_test_user
    password = "password123"
    registration.sign_up(user, password, password)
    registration.check_registration_message()


# 5. Тест регистрации с несовпадающими паролями
@allure.story('Registration with mismatched passwords')
def test_registration_mismatched_password(page: Page, generate_test_user: str) -> None:
    registration = RegistrationPage(page)
    registration.register_button.click()
    new_user = generate_test_user
    registration.sign_up(new_user, "password123", "different123")
    registration.check_error_message()


# 6. Тест регистрации с уже существующим пользователем
@allure.story('Registration with existing user')
def test_registration_existing_user(page: Page, envs) -> None:
    registration = RegistrationPage(page)
    registration.register_button.click()
    registration.sign_up(envs.test_username, envs.test_password, envs.test_password)
    registration.check_error_message(envs.test_username)


# 7. Тест проверки заголовков на странице расходов
@allure.story('Spending page titles')
@Pages.main_page
def test_spending_page_titles(page: Page) -> None:
    spending_page = SpendingPage(page)
    spending_page.check_spending_page_titles()


# 8. Тест создания расхода
@allure.story('Create spending')
@Pages.main_page
@TestData.category(Category.SCHOOL)
@TestData.spends(
    SpendAdd(
        amount=100,
        description=f"Test spending {int(time.time())}",
        category=Category.SCHOOL,
        spendDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        currency="RUB"
    )
)
def test_create_spending(page: Page, category: str, spends) -> None:
    spending_page = SpendingPage(page)
    page.reload()

    spending_page.check_spending_exists(
        category=category,
        amount=spends.amount,
        description=spends.description
    )


# 9. Тест фильтрации расходов
@allure.story('Spending filters')
@Pages.main_page
@TestData.category(Category.SCHOOL)
@TestData.spends(
    SpendAdd(
        amount=108.51,
        description="Test filter",
        category=Category.SCHOOL,
        spendDate="2025-03-18T00:01:27.955Z",
        currency="RUB"
    )
)
def test_spending_filters(page: Page, category: str, spends) -> None:
    spending_page = SpendingPage(page)
    page.reload()

    spending_page.filter_by_period("all")
    expect(spending_page.spending_table).to_be_visible()
    spending_page.check_spending_exists(
        category=category,
        amount=spends.amount,
        description=spends.description
    )

    spending_page.filter_by_period("today")
    expect(spending_page.spending_table).to_be_visible()
    spending_page.check_spending_not_exists(spends.description)


# 10. Тест удаления расходов
@allure.story('Delete spending')
@Pages.main_page
@TestData.category(Category.SCHOOL)
@TestData.spends(
    SpendAdd(
        amount=100,
        description=f"To be deleted {int(time.time())}",
        category=Category.SCHOOL,
        spendDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        currency="RUB"
    )
)
def test_delete_spending(page: Page, category: str, spends, spends_client: SpendsHttpClient) -> None:
    page.reload()
    spending_page = SpendingPage(page)
    spending_page.check_spending_exists(
        category=category,
        amount=spends.amount,
        description=spends.description
    )

    spends_client.remove_spends([spends.id])
    page.reload()
    spending_page.check_spending_not_exists(spends.description)


# 11. Тест создания расхода с максимальными значениями
@allure.story('Create spending with max values')
@Pages.main_page
@TestData.category(Category.SCHOOL)
@TestData.spends(
    SpendAdd(
        amount=999999.99,
        description="a" * 255,
        category=Category.SCHOOL,
        spendDate=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        currency="RUB"
    )
)
def test_create_max_values_spending(page: Page, category: str, spends) -> None:
    spending_page = SpendingPage(page)
    page.reload()

    spending_page.check_spending_exists(
        category=category,
        amount=spends.amount,
        description=spends.description
    )


# 12. Тест проверки статистики
@allure.story('Statistics')
@Pages.main_page
@TestData.category(Category.SCHOOL)
@TestData.spends(
    SpendAdd(
        amount=108.51,
        description="Test statistics",
        category=Category.SCHOOL,
        spendDate="2025-03-18T00:01:27.955Z",
        currency="RUB"
    )
)
def test_statistics(page: Page, category: str, spends) -> None:
    spending_page = SpendingPage(page)
    page.reload()

    spending_page.check_statistics_visible()
    spending_page.check_spending_exists(
        category=category,
        amount=spends.amount,
        description=spends.description
    )


# 13. Тест валидации формы расходов
@allure.story('Spending form validation')
@Pages.main_page
@TestData.category(Category.SCHOOL)
@TestData.spends(
    SpendAdd(
        amount=108.51,
        description="Test form validation",
        category=Category.SCHOOL,
        spendDate="2025-03-18T00:01:27.955Z",
        currency="RUB"
    )
)
def test_spending_form_validation(page: Page, category: str, spends) -> None:
    spending_page = SpendingPage(page)
    page.reload()

    spending_page.check_form_validation()


# 14. Тест наличие кнопок меню
@allure.story('Navigation buttons')
@Pages.main_page
def test_navigation_buttons(page: Page) -> None:
    spending_page = SpendingPage(page)
    spending_page.check_navigation_buttons()


# 15. Тест наличия картинки
@allure.story('Gringotts image visible')
@Pages.main_page
def test_gringotts_image_visible(page: Page) -> None:
    spending_page = SpendingPage(page)
    spending_page.check_gringotts_image()


# 16. Тест выхода из системы
@allure.story('Logout')
@Pages.main_page
def test_logout(page: Page) -> None:
    login = LoginPage(page)
    page.click(".header__logout")
    expect(login.login_button).to_be_visible()
