from playwright.sync_api import Page, expect
from .pages.login_page import LoginPage
from .pages.registration_page import RegistrationPage
from .pages.spending_page import SpendingPage
from .pages.profile_page import ProfilePage
from marks import Pages, TestData
from datetime import datetime
import time
from typing import Dict, Tuple, Any, List, Optional
from clients.spends_client import SpendsHttpClient


# 1. Тест успешного логина
def test_successful_login(page: Page, app_user: Tuple[str, str]) -> None:
    username, password = app_user
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in(username, password)
    spending = SpendingPage(page)
    spending.check_spending_page_titles()


# 2. Тест логина несуществующего пользователя
def test_non_existent_user_login(page: Page) -> None:
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in("invalid_user", "invalid_password")
    login.check_error_message()


# 3. Тест логина с неправильным паролем
def test_login_wrong_password(page: Page, app_user: Tuple[str, str]) -> None:
    username, _ = app_user
    login = LoginPage(page)
    login.login_button.click()
    login.sign_in(username, "wrong_password")
    login.check_error_message()


# 4. Тест успешной регистрации
def test_successful_registration(page: Page, generate_test_user: str) -> None:
    registration = RegistrationPage(page)
    registration.register_button.click()
    user = generate_test_user
    password = "password123"
    registration.sign_up(user, password, password)
    registration.check_registration_message()


# 5. Тест регистрации с несовпадающими паролями
def test_registration_mismatched_password(page: Page, generate_test_user: str) -> None:
    registration = RegistrationPage(page)
    registration.register_button.click()
    new_user = generate_test_user
    registration.sign_up(new_user, "password123", "different123")
    registration.check_error_message()


# 6. Тест регистрации с уже существующим пользователем
def test_registration_existing_user(page: Page, app_user: Tuple[str, str]) -> None:
    username, password = app_user
    registration = RegistrationPage(page)
    registration.register_button.click()
    registration.sign_up(username, password, password)
    registration.check_error_message(username)


# 7. Тест проверки заголовков на странице расходов
@Pages.main_page
def test_spending_page_titles(page: Page) -> None:
    spending = SpendingPage(page)
    spending.check_spending_page_titles()


# 8. Тест создания расхода
@Pages.main_page
@TestData.category("Products")
def test_create_spending(page: Page, category: str, spends_client: SpendsHttpClient) -> None:
    spending = SpendingPage(page)
    description = f"Test spending {int(time.time())}"

    spend_data: Dict[str, str] = {
        "amount": "100",
        "category": category,
        "description": description,
        "spendDate": datetime.utcnow().strftime("%Y-%m-%d"),
        "currency": "RUB"
    }
    spend = spends_client.add_spends(spend_data)

    page.reload()

    spending.check_spending_exists(
        category=category,
        amount=spend_data["amount"],
        description=description
    )


# 9. Тест фильтрации расходов
@Pages.main_page
@TestData.category("Products")
@TestData.spends({
    "amount": "100",
    "description": "Filter test",
    "category": "Products",
    "spendDate": "2025-03-17",
    "currency": "RUB"
})
def test_spending_filters(page: Page, spends: Dict[str, str], category: str) -> None:
    spending_page = SpendingPage(page)

    spending_page.filter_by_period("all")
    expect(spending_page.spending_table).to_be_visible()
    spending_page.check_spending_exists(
        amount=spends["amount"],
        category=category,
        description=spends["description"]
    )

    spending_page.filter_by_period("today")
    expect(spending_page.spending_table).to_be_visible()
    spending_page.check_spending_not_exists(spends["description"])


# 10. Полный user flow через API
@Pages.main_page
def test_user_flow(page: Page, app_user: Tuple[str, str], spends_client: SpendsHttpClient) -> None:
    timestamp = int(time.time())
    category_name = f"Test Category {timestamp}"
    spends_client.add_category(category_name)

    description = f"Flow test {timestamp}"
    spend_data: Dict[str, str] = {
        "amount": "50",
        "category": category_name,
        "description": description,
        "spendDate": datetime.utcnow().strftime("%Y-%m-%d"),
        "currency": "RUB"
    }
    spend = spends_client.add_spends(spend_data)

    page.reload()

    spending = SpendingPage(page)
    spending.check_spending_exists(
        category=category_name,
        amount=spend_data["amount"],
        description=description
    )

    spends_client.remove_spends([spend["id"]])

    page.reload()
    spending.check_spending_not_exists(description)


# 11. Тест создания нескольких категорий
@Pages.main_page
def test_multiple_categories_creation(page: Page, spends_client: SpendsHttpClient) -> None:
    profile = ProfilePage(page)
    profile.navigate_to_profile()
    
    categories: List[str] = ["Food", "Transport", "Entertainment"]
    for category in categories:
        spends_client.add_category(category)

    page.reload()

    current_categories = spends_client.get_categories()
    for category in categories:
        assert any(cat["category"] == category for cat in current_categories)


# 12. Тест удаления расходов
@Pages.main_page
@TestData.category("Products")
def test_delete_spending(page: Page, category: str, spends_client: SpendsHttpClient) -> None:
    description = f"To be deleted {int(time.time())}"

    spend_data: Dict[str, str] = {
        "amount": "100",
        "category": category,
        "description": description,
        "spendDate": datetime.utcnow().strftime("%Y-%m-%d"),
        "currency": "RUB"
    }
    spend = spends_client.add_spends(spend_data)

    page.reload()

    spending_page = SpendingPage(page)
    spending_page.check_spending_exists(
        category=category,
        amount=spend_data["amount"],
        description=description
    )

    spends_client.remove_spends([spend["id"]])

    page.reload()

    spending_page.check_spending_not_exists(description)


# 13. Тест создания категории и расхода через API
@Pages.main_page
def test_api_category_and_spending(page: Page, spends_client: SpendsHttpClient) -> None:
    timestamp = int(time.time())
    category_name = f"Test Category {timestamp}"
    spends_client.add_category(category_name)

    description = f"API Spending {timestamp}"
    spend_data: Dict[str, str] = {
        "amount": "200",
        "category": category_name,
        "description": description,
        "spendDate": datetime.utcnow().strftime("%Y-%m-%d"),
        "currency": "RUB"
    }
    spend = spends_client.add_spends(spend_data)
    page.reload()
    spending_page = SpendingPage(page)
    spending_page.check_spending_exists(
        category=category_name,
        amount=spend_data["amount"],
        description=description
    )

    spends_client.remove_spends([spend["id"]])
    page.reload()
    spending_page.check_spending_not_exists(description)


# 14. Тест создания расхода с максимальными значениями
@Pages.main_page
@TestData.category("Products")
def test_create_max_values_spending(page: Page, category: str) -> None:
    spending = SpendingPage(page)
    description = "a" * 255
    amount = "999999.99"
    
    test_spending = spending.create_spending(
        amount=amount,
        category=category,
        description=description
    )
    
    spending.check_spending_exists(
        category=test_spending["category"],
        description=test_spending["description"]
    )


# 15. Тест фильтрации по нескольким периодам
@Pages.main_page
@TestData.category("Products")
@TestData.spends({
    "amount": "100",
    "description": "Period test",
    "category": "Products",
    "spendDate": datetime.utcnow().strftime("%Y-%m-%d"),
    "currency": "RUB"
})
def test_multiple_period_filters(page: Page, spends: Dict[str, str], category: str) -> None:
    spending_page = SpendingPage(page)
    periods: List[str] = ["today", "week", "month", "all"]
    
    for period in periods:
        spending_page.filter_by_period(period)
        expect(spending_page.spending_table).to_be_visible()
        spending_page.check_spending_exists(
            category=category,
            amount=spends["amount"],
            description=spends["description"],
            currency=spends["currency"]
        )


# 16. Тест создания расходов в разных валютах
@Pages.main_page
@TestData.category("Products")
def test_multiple_currency_spending(page: Page, category: str) -> None:
    spending_page = SpendingPage(page)
    profile_page = ProfilePage(page)
    currencies: List[str] = ["RUB", "USD", "EUR"]
    
    for currency in currencies:
        profile_page.navigate_to_profile()
        profile_page.change_currency(currency)
        profile_page.navigate_to_main()
        timestamp = int(time.time())
        description = f"Currency test {currency} {timestamp}"

        spending_page.create_spending(
            amount=100,
            category=category,
            description=description
        )

        spending_page.check_spending_exists(
            amount=100,
            category=category,
            description=description
        )

        expect(page.locator(f"text={description}")).to_be_visible()


# 17. Тест проверки статистики
@Pages.main_page
@TestData.category("Products")
def test_statistics(page: Page, category: str) -> None:
    timestamp = int(time.time())
    description = f"Stats test {timestamp}"

    spending_page = SpendingPage(page)
    spending_page.create_spending(
        amount=100,
        category=category,
        description=description
    )

    spending_page.check_statistics_visible()
    spending_page.check_spending_exists(
        category=category,
        description=description
    )


# 18. Тест валидации формы расходов
@Pages.main_page
def test_spending_form_validation(page: Page) -> None:
    spending_page = SpendingPage(page)
    spending_page.check_form_validation()


# 19. Тест наличие кнопок меню
@Pages.main_page
def test_navigation_buttons(page: Page) -> None:
    spending_page = SpendingPage(page)
    spending_page.check_navigation_buttons()


# 20. Тест наличия картинки
@Pages.main_page
def test_gringotts_image_visible(page: Page) -> None:
    spending_page = SpendingPage(page)
    spending_page.check_gringotts_image()


# 21. Тест выхода из системы
@Pages.main_page
def test_logout(page: Page) -> None:
    login = LoginPage(page)
    page.click(".header__logout")
    expect(login.login_button).to_be_visible()
