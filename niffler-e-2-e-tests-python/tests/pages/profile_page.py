from playwright.sync_api import Page, expect


class ProfilePage:
    def __init__(self, page: Page):
        self.page = page
        self.profile_link = page.locator('[data-tooltip-content="Profile"]')
        self.main_link = page.locator('[data-tooltip-content="Main page"]')
        self.category_input = page.locator('input[name="category"]')
        self.create_category_button = page.locator('button:text("Create")')
        self.categories_list = page.locator('.main-content__section-categories')
        self.no_categories_message = page.locator('text="No spending categories yet!"')
        self.currency_select_container = page.locator('.select-wrapper')
        self.currency_select = page.locator('[id^="react-select"][id$="-input"]').nth(0)

    def navigate_to_profile(self):
        self.profile_link.click()
        expect(self.page).to_have_url("http://frontend.niffler.dc/profile")
        expect(self.category_input).to_be_visible()

    def navigate_to_main(self):
        self.main_link.click()
        expect(self.page).to_have_url("http://frontend.niffler.dc/main")
        self.page.reload()

    def add_category(self, category_name: str):
        expect(self.category_input).to_be_visible()
        self.category_input.fill(category_name)
        self.create_category_button.click()
        expect(self.no_categories_message).not_to_be_visible()
        expect(self.categories_list).to_contain_text(category_name)
        
    def change_currency(self, currency: str):
        expect(self.currency_select_container).to_be_visible()
        self.currency_select_container.click()
        expect(self.currency_select).to_be_visible()
        self.currency_select.fill(currency)
        self.currency_select.press("Enter")
