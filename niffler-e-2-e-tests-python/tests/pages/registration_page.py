from playwright.sync_api import Page, expect


class RegistrationPage:
    def __init__(self, page: Page):
        self.page = page
        self.register_button = page.locator('a.main__link:text("Register")')
        self.username_input = page.locator('input[name="username"]')
        self.password_input = page.locator('input[name="password"]')
        self.submit_password_input = page.locator('input[name="passwordSubmit"]')
        self.signup_button = page.locator('button.form__submit')
        self.registration_message = page.locator('.form__paragraph:text-matches("Congratulations")')
        self.error_message = page.locator('.form__error')
        self.sign_in_button = page.locator('a:text("Sign in!")')

    def sign_up(self, user: str, password: str, submit_password: str):
        expect(self.username_input).to_be_empty()
        self.username_input.fill(user)
        expect(self.password_input).to_be_empty()
        self.password_input.fill(password)
        expect(self.submit_password_input).to_be_empty()
        self.submit_password_input.fill(submit_password)
        self.signup_button.click()

    def check_registration_message(self):
        expect(self.registration_message).to_contain_text("Congratulations! You've registered")

    def check_error_message(self, username: str = None):
        if username:
            expect(self.error_message).to_contain_text(f'Username `{username}` already exists')
        else:
            expect(self.error_message).to_contain_text('Passwords should be equal')
