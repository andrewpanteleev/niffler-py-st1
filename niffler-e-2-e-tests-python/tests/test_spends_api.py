import pytest
import allure
from datetime import datetime
import uuid
import json
import requests

from models.spend import SpendAdd
from models.enums import Category


@allure.feature("API Categories")
class TestCategories:
    @allure.title("Добавление новой категории")
    def test_add_category(self, spends_client):
        category_name = f"test_category_{uuid.uuid4().hex[:8]}"
        new_category = spends_client.add_category(category_name)

        assert new_category.category == category_name
        assert new_category.id is not None
        assert new_category.username is not None

        all_categories = spends_client.get_categories()
        category_ids = [c.id for c in all_categories]
        assert new_category.id in category_ids, "Новая категория не найдена в общем списке"

    @allure.title("Получение всех категорий")
    def test_get_all_categories(self, spends_client):
        categories = spends_client.get_categories()

        assert len(categories) > 0, "Список категорий пуст"
        for category in categories:
            assert category.id is not None
            assert category.category is not None
            assert category.username is not None


@allure.feature("API Spends")
class TestSpends:
    @allure.title("Добавление новой траты")
    def test_add_spend(self, spends_client):
        categories = spends_client.get_categories()
        assert len(categories) > 0, "Нет категорий для создания траты"

        spend_data = SpendAdd(
            amount=100.50,
            description="Test spend",
            category=categories[0].category,
            spendDate=datetime.now().strftime("%Y-%m-%d"),
            currency="RUB"
        )

        new_spend = spends_client.add_spends(spend_data)

        assert new_spend.id is not None
        assert new_spend.amount == spend_data.amount
        assert new_spend.description == spend_data.description
        assert new_spend.currency == spend_data.currency

        spends_client.remove_spends([new_spend.id])


    @allure.title("Получение всех трат пользователя")
    def test_get_all_spends(self, spends_client):
        spends = spends_client.get_spends()

        for spend in spends:
            assert spend.id is not None
            assert isinstance(spend.amount, float)
            assert isinstance(spend.description, str)

            if spend.category_id:
                assert isinstance(spend.category_id, str)
            assert spend.currency is not None
            assert spend.username is not None



    @allure.title("Добавление траты с минимальной суммой")
    def test_add_spend_with_min_amount(self, spends_client):
        categories = spends_client.get_categories()

        spend_data = SpendAdd(
            amount=0.01,
            description="Minimal amount spend",
            category=categories[0].category,
            spendDate=datetime.now().strftime("%Y-%m-%d"),
            currency="RUB"
        )
        
        new_spend = spends_client.add_spends(spend_data)
        assert new_spend.amount == 0.01

        spends_client.remove_spends([new_spend.id])

    @allure.title("Добавление траты с большой суммой")
    def test_add_spend_with_large_amount(self, spends_client):
        categories = spends_client.get_categories()

        spend_data = SpendAdd(
            amount=999999.99,
            description="Large amount spend",
            category=categories[0].category,
            spendDate=datetime.now().strftime("%Y-%m-%d"),
            currency="RUB"
        )
        
        new_spend = spends_client.add_spends(spend_data)
        assert new_spend.amount == 999999.99

        spends_client.remove_spends([new_spend.id])

    @allure.title("Добавление траты с длинным описанием")
    def test_add_spend_with_long_description(self, spends_client):
        categories = spends_client.get_categories()

        long_description = "A" * 255
        spend_data = SpendAdd(
            amount=100.0,
            description=long_description,
            category=categories[0].category,
            spendDate=datetime.now().strftime("%Y-%m-%d"),
            currency="RUB"
        )
        
        new_spend = spends_client.add_spends(spend_data)
        assert new_spend.description == long_description

        spends_client.remove_spends([new_spend.id])

    @allure.title("Удаление траты")
    def test_remove_spend(self, spends_client):
        categories = spends_client.get_categories()
        
        spend_data = SpendAdd(
            amount=50.0,
            description="Spend to be deleted",
            category=categories[0].category,
            spendDate=datetime.now().strftime("%Y-%m-%d"),
            currency="RUB"
        )

        new_spend = spends_client.add_spends(spend_data)
        spend_id = new_spend.id

        all_spends_before = spends_client.get_spends()
        spend_ids_before = [s.id for s in all_spends_before]
        assert spend_id in spend_ids_before

        spends_client.remove_spends([spend_id])

        all_spends_after = spends_client.get_spends()
        spend_ids_after = [s.id for s in all_spends_after]
        assert spend_id not in spend_ids_after

    @allure.title("Проверка ограничений валюты")
    def test_currency_restrictions(self, spends_client):
        """
        Тест проверяет, что траты можно создавать только в валюте пользователя (RUB),
        и что попытка создать трату в другой валюте приводит к ошибке 400
        """
        categories = spends_client.get_categories()

        spend_data_rub = SpendAdd(
            amount=100.0,
            description="Spend in RUB",
            category=categories[0].category,
            spendDate=datetime.now().strftime("%Y-%m-%d"),
            currency="RUB"
        )
        
        new_spend = spends_client.add_spends(spend_data_rub)
        assert new_spend.currency == "RUB"

        spends_client.remove_spends([new_spend.id])

        try:
            spend_data_usd = SpendAdd(
                amount=100.0,
                description="Spend in USD",
                category=categories[0].category,
                spendDate=datetime.now().strftime("%Y-%m-%d"),
                currency="USD"
            )
            spends_client.add_spends(spend_data_usd)
            pytest.fail("Ожидалась ошибка 400 при создании траты в USD")
        except requests.HTTPError as e:
            assert e.response.status_code == 400
            error_json = json.loads(e.response.text)
            assert "Spending currency should be same with user currency" == error_json["detail"]

    @allure.title("Добавление нескольких трат и удаление их одним запросом")
    def test_add_multiple_spends_and_remove(self, spends_client):
        categories = spends_client.get_categories()
        created_spend_ids = []

        for i in range(3):
            spend_data = SpendAdd(
                amount=100.0 + i,
                description=f"Multiple spend {i}",
                category=categories[0].category,
                spendDate=datetime.now().strftime("%Y-%m-%d"),
                currency="RUB"
            )
            
            new_spend = spends_client.add_spends(spend_data)
            created_spend_ids.append(new_spend.id)

        all_spends = spends_client.get_spends()
        for spend_id in created_spend_ids:
            assert any(s.id == spend_id for s in all_spends)

        spends_client.remove_spends(created_spend_ids)

        all_spends_after = spends_client.get_spends()
        for spend_id in created_spend_ids:
            assert not any(s.id == spend_id for s in all_spends_after) 