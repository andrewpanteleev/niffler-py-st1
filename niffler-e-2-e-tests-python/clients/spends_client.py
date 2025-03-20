from urllib.parse import urljoin
from models.spend import Category, Spend, SpendAdd

import requests


class SpendsHttpClient:
    session: requests.Session
    base_url: str

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.session = requests.session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

    def get_categories(self) -> list[Category]:
        response = self.session.get(urljoin(self.base_url, "/api/categories/all"))
        self.raise_for_status(response)
        return [Category.model_validate(item) for item in response.json()]

    def add_category(self, name: str) -> Category:
        response = self.session.post(urljoin(self.base_url, "/api/categories/add"), json={
            "category": name
        })
        self.raise_for_status(response)
        return Category.model_validate(response.json())

    def get_spends(self) -> list[Spend]:
        url = urljoin(self.base_url, "/api/spends/all")
        response = self.session.get(url)
        self.raise_for_status(response)
        return [Spend.model_validate(item) for item in response.json()]

    def add_spends(self, spend: SpendAdd) -> Spend:
        url = urljoin(self.base_url, "/api/spends/add")
        response = self.session.post(url, json=spend.model_dump())
        self.raise_for_status(response)
        return Spend.model_validate(response.json())

    def remove_spends(self, ids: list[str]):
        url = urljoin(self.base_url, "/api/spends/remove")
        response = self.session.delete(url, params={"ids": ids})
        self.raise_for_status(response)

    @staticmethod
    def raise_for_status(response: requests.Response):
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 400:
                e.add_note(response.text)
                raise

