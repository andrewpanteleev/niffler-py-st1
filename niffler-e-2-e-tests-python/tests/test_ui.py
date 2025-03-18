import pytest
from playwright.sync_api import Page, expect
from .pages.login_page import LoginPage
from .pages.registration_page import RegistrationPage
from .pages.spending_page import SpendingPage
from .pages.profile_page import ProfilePage
import time


# 1. Тест успешного логина
def test_successful_login(page: Page, credentials):
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in(credentials["user"], credentials["password"])
    spending = SpendingPage(page)
    spending.check_spending_page_titles()


# 2. Тест логина несуществующего пользователя
def test_non_existent_user_login(page: Page):
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in("invalid_user", "invalid_password")
    login.check_error_message()


# 3. Тест логина с неправильным паролем
def test_login_wrong_password(page: Page, credentials):
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in(credentials["user"], "wrong_password")
    login.check_error_message()


# 4. Тест успешной регистрации
def test_successful_registration(page: Page, generate_test_user):
    registration = RegistrationPage(page)
    registration.register_button.click()
    user = generate_test_user
    password = "password123"
    registration.sign_up(user, password, password)
    registration.check_registration_message()


# 5. Тест регистрации с несовпадающими паролями
def test_registration_mismatched_password(page: Page, generate_test_user):
    registration = RegistrationPage(page)
    registration.register_button.click()
    new_user = generate_test_user
    registration.sign_up(new_user, "password123", "different123")
    registration.check_error_message()


# 6. Тест регистрации с уже существующим пользователем
def test_registration_existing_user(page: Page, credentials, generate_test_user):
    registration = RegistrationPage(page)
    registration.register_button.click()
    registration.sign_up(credentials["user"], credentials["password"], credentials["password"])
    registration.check_error_message(credentials["user"])


# 7. Тест проверки заголовков на странице расходов
def test_spending_page_titles(page: Page, credentials):
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in(credentials["user"], credentials["password"])
    spending = SpendingPage(page)
    spending.check_spending_page_titles()


# 8. Тест создания расхода
def test_create_spending(page: Page, credentials):
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in(credentials["user"], credentials["password"])

    spending = SpendingPage(page)
    test_spending = spending.create_spending(
        amount=100,
        category="Products",
        description="Test spending"
    )

    spending.check_spending_exists(
        category=test_spending["category"],
        amount=test_spending["amount"],
        description=test_spending["description"]
    )


# 9. Тест фильтрации расходов
def test_spending_filters(page: Page, credentials):
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in(credentials["user"], credentials["password"])
    
    spending = SpendingPage(page)

    test_spending = spending.create_spending(
        amount=100,
        category="Products",
        description="Filter test " + str(int(time.time()))
    )

    spending.filter_by_period("today")
    expect(spending.spending_table).to_be_visible()

    spending.filter_by_category(test_spending["category"])
    expect(spending.spending_table).to_be_visible()

    spending.check_spending_exists(
        category=test_spending["category"],
        amount=test_spending["amount"],
        description=test_spending["description"]
    )


# 10. Полный user flow: регистрация, логин, создание категории и расхода
def test_user_flow(page: Page, generate_test_user):
    registration = RegistrationPage(page)
    registration.register_button.click()
    new_user = generate_test_user
    password = "password123"
    registration.sign_up(new_user, password, password)
    registration.check_registration_message()
    registration.sign_in_button.click()

    login = LoginPage(page)
    login.sign_in(new_user, password)

    profile = ProfilePage(page)
    profile.navigate_to_profile()
    profile.add_category("Products")
    profile.navigate_to_main()

    spending = SpendingPage(page)
    spending.check_spending_page_titles()

    test_spending = spending.create_spending(
        amount=50,
        category="Products",
        description="Flow test " + str(int(time.time()))
    )

    spending.check_spending_exists(
        category=test_spending["category"],
        amount=test_spending["amount"],
        description=test_spending["description"]
    )
