from playwright.sync_api import Page, expect
from typing import Union, Optional
from allure import step


class SpendingPage:
    def __init__(self, page: Page):
        self.page = page
        # Заголовки и основные элементы
        self.add_spending_title = page.locator('.main-content__section-add-spending h2')
        self.history_title = page.locator('.main-content__section-history h2')
        self.statistics_canvas = page.locator('canvas')

        # Кнопки меню
        self.main_page_button = page.locator('[data-tooltip-id="main"]')
        self.friends_button = page.locator('[data-tooltip-id="friends"]')
        self.all_people_button = page.locator('[data-tooltip-id="people"]')
        self.profile_button = page.locator('[data-tooltip-id="profile"]')
        
        # Форма добавления расхода
        self.amount_input = page.locator('input[name="amount"]')
        self.category_select = page.locator('#react-select-3-input')
        self.description_input = page.locator('input[name="description"]')
        self.add_spending_button = page.locator('button:text("Add new spending")')
        self.date_input = page.locator('.react-datepicker__input-container input')
        self.currency_select = page.locator('#react-select-4-input')
        
        # Таблица расходов
        self.spending_container = page.locator('.spendings__content')
        self.spending_table = page.locator('.spendings-table')
        self.no_spendings_message = page.locator('text="No spendings provided yet!"')
        
        # Фильтры
        self.today_filter = page.locator('button:text("Today")')
        self.last_week_filter = page.locator('button:text("Last week")')
        self.last_month_filter = page.locator('button:text("Last month")')
        self.all_time_filter = page.locator('button:text("All time")')
        self.category_filter = page.locator('#react-select-5-input')

        self.new_spending_button = page.locator('button:text("New spending")')
        self.submit_button = page.locator('button:text("Add new spending")')
        
        # Раздел статистики
        self.statistics_section = page.locator(".main-content__section-stats")
        
        # Сообщения валидации формы
        self.category_required_message = page.locator("text=Category is required")
        self.amount_required_message = page.locator("text=Amount is required")
        self.date_required_message = page.locator("text=Spend date is required")

        # Картинки
        self.gringotts_image = page.locator('img.spendings__img')

    @step("UI: Check spending page titles")
    def check_spending_page_titles(self):
        expect(self.add_spending_title).to_contain_text("Add new spending")
        expect(self.history_title).to_contain_text("History of spendings")
        expect(self.statistics_canvas).to_be_visible()

    @step("UI: Check navigation buttons")
    def check_navigation_buttons(self):
        expect(self.main_page_button).to_be_visible()
        expect(self.friends_button).to_be_visible()
        expect(self.all_people_button).to_be_visible()
        expect(self.profile_button).to_be_visible()

    @step("UI: Check gringotts image visibility")
    def check_gringotts_image(self):
        expect(self.gringotts_image).to_be_visible()

    @step("UI: Check that spending exists")
    def check_spending_exists(
        self,
        category: str,
        description: Optional[str] = None,
        amount: Union[int, str] = None,
        currency: str = "RUB"
    ):
        expect(self.no_spendings_message).not_to_be_visible()
        expect(self.spending_table).to_be_visible()

        selector = f"tr:has-text('{category}')"
        if description:
            selector += f":has-text('{description}')"

        row_locator = self.spending_table.locator(selector).first
        expect(row_locator).to_be_visible()

    @step("UI: Check that spending does not exist")
    def check_spending_not_exists(self, description: str):
        description_locator = self.page.locator(f"text={description}")
        expect(description_locator).not_to_be_visible()

    @step("UI: Filter spendings by period")
    def filter_by_period(self, period: str):
        period_map = {
            "today": self.today_filter,
            "week": self.last_week_filter,
            "month": self.last_month_filter,
            "all": self.all_time_filter
        }
        period_map[period.lower()].click()

    @step("UI: Check statistics visibility")
    def check_statistics_visible(self):
        expect(self.statistics_section).to_be_visible()
        expect(self.statistics_canvas).to_be_visible()

    @step("UI: Check spending form validation")
    def check_form_validation(self):
        self.add_spending_button.click()
        expect(self.category_required_message).to_be_visible()
        self.category_select.click()
        self.category_select.fill("School")
        self.category_select.press("Enter")
        self.add_spending_button.click()
        expect(self.amount_required_message).to_be_visible()
        self.amount_input.fill("100")
        self.date_input.clear()
        self.add_spending_title.click()
        self.add_spending_button.click()
        expect(self.date_required_message).to_be_visible()
