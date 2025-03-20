from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.login_button = page.locator('a.main__link:text("Login")')
        self.username_input = page.locator('input[name="username"]')
        self.password_input = page.locator('input[name="password"]')
        self.signin_button = page.locator('button[type="submit"]')
        self.create_new_user_button = page.locator('.form__register')
        self.error_message = page.locator("p.form__error")


    def sign_in(self, envs):
        expect(self.username_input).to_be_visible()
        self.username_input.fill(envs.test_username)
        expect(self.password_input).to_be_visible()
        self.password_input.fill(envs.test_password)
        self.signin_button.click()


    def sign_in_non_existent_user_login(self, envs):
        expect(self.username_input).to_be_visible()
        self.username_input.fill(envs.invalid_user)
        expect(self.password_input).to_be_visible()
        self.password_input.fill(envs.invalid_password)
        self.signin_button.click()


    def sign_in_wrong_password(self, envs):
        expect(self.username_input).to_be_visible()
        self.username_input.fill(envs.test_username)
        expect(self.password_input).to_be_visible()
        self.password_input.fill(envs.invalid_password)
        self.signin_button.click()


    def check_error_message(self):
        expect(self.error_message).to_be_visible()
