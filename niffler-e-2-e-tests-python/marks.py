import pytest
from typing import Any, Dict, Callable, TypeVar, List, Union, Optional


T = TypeVar('T', bound=Callable[..., Any])


class Pages:
    main_page = pytest.mark.usefixtures("main_page")


class TestData:
    @staticmethod
    def category(x: str) -> Callable[[T], T]:
        return pytest.mark.parametrize("category", [x], indirect=True)
    
    @staticmethod
    def spends(x: Dict[str, Any]) -> Callable[[T], T]:
        return pytest.mark.parametrize("spends", [x], indirect=True, ids=lambda param: param["description"])