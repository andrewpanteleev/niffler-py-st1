from playwright.sync_api import Page, expect


class SpendingPage:
    def __init__(self, page: Page):
        self.page = page
        # Заголовки и основные элементы
        self.add_spending_title = page.locator('.main-content__section-add-spending h2')
        self.history_title = page.locator('.main-content__section-history h2')
        self.statistics_canvas = page.locator('canvas')
        
        # Форма добавления расхода
        self.amount_input = page.locator('input[name="amount"]')
        self.category_select = page.locator('#react-select-3-input')  # Select для категории
        self.description_input = page.locator('input[name="description"]')
        self.add_spending_button = page.locator('button:text("Add new spending")')
        self.date_input = page.locator('.react-datepicker__input-container input')
        
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

    def check_spending_page_titles(self):
        expect(self.add_spending_title).to_contain_text("Add new spending")
        expect(self.history_title).to_contain_text("History of spendings")
        expect(self.statistics_canvas).to_be_visible()

    def create_spending(self, amount: int, category: str, description: str = None):
        self.amount_input.fill(str(amount))

        self.category_select.click()
        self.category_select.fill(category)
        self.category_select.press("Enter")

        if description:
            self.description_input.fill(description)

        self.add_spending_button.click()

        return {
            "amount": amount,
            "category": category,
            "description": description
        }

    def check_spending_exists(self, category: str, amount: int, description: str = None):
        expect(self.no_spendings_message).not_to_be_visible()
        expect(self.spending_table).to_be_visible()

        selector = f"tr:has-text('{category}'):has-text('{amount}')"
        if description:
            selector += f":has-text('{description}')"

        row_locator = self.spending_table.locator(selector).first
        expect(row_locator).to_be_visible()

    def filter_by_period(self, period: str):
        period_map = {
            "today": self.today_filter,
            "last_week": self.last_week_filter,
            "last_month": self.last_month_filter,
            "all_time": self.all_time_filter
        }
        period_map[period.lower()].click()

    def filter_by_category(self, category: str):
        self.category_filter.click()
        self.category_filter.fill(category)
        self.category_filter.press("Enter")
