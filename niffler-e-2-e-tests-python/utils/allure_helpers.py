import allure
import json
import logging
import os
from json import JSONDecodeError

import curlify
from allure_commons.types import AttachmentType
from requests import Response
from jinja2 import Environment, FileSystemLoader, select_autoescape


def allure_attach_request(function):
    """Декоратор логироваания запроса, хедеров запроса, хедеров ответа в allure шаг и аллюр аттачмент и в консоль."""

    def wrapper(*args, **kwargs):

        method, url = args[1], args[2]
        # self_ = args[0]
        # headers = kwargs.get('headers', None)
        # files = kwargs.get('files', None)
        # data = kwargs.get('data', None)
        # params = kwargs.get('params', None)
        # auth = kwargs.get('auth', None)
        # cookies = kwargs.get('cookies', None)
        # hooks = kwargs.get('hooks', None)
        # json_ = kwargs.get('json', None)
        # request = Request(
        #     method=method.upper(),
        #     url=self_.base_url + url,
        #     headers=headers,
        #     files=files,
        #     data=data or {},
        #     json=json_,
        #     params=params or {},
        #     auth=auth,
        #     cookies=cookies,
        #     hooks=hooks,
        # )
        # req = PreparedRequest()
        # req.prepare(method=request.method.upper(),
        #     url=request.url,
        #     files=request.files,
        #     data=request.data,
        #     json=request.json,
        #     headers=merge_setting(
        #         request.headers, self_.headers, dict_class=CaseInsensitiveDict
        #     ),
        #     params=merge_setting(request.params, self_.params),
        #     auth=merge_setting(auth, self_.auth),
        #     cookies=merge_cookies(
        #     merge_cookies(RequestsCookieJar(), self_.cookies), cookies
        # ),
        #     hooks=merge_hooks(request.hooks, self_.hooks),)

        # Получаем путь к директории templates относительно текущего файла
        current_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(os.path.dirname(current_dir), 'templates')
        
        env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape()
        )
        template = env.get_template("http-colored-request.ftl")
        # template = env.get_template("http-request.ftl")

        with allure.step(f"{method} {url}"):

            response: Response = function(*args, **kwargs)
            curl = curlify.to_curl(response.request)

            prepare_render = {
                "request": response.request,
                "curl": curl,
            }
            render = template.render(prepare_render)

            allure.attach(
                body=render,
                name=f"Request",
                attachment_type=AttachmentType.HTML,
                extension=".html"
            )
            try:
                allure.attach(
                    body=json.dumps(response.json(), indent=4).encode("utf8"),
                    name=f"Response json {response.status_code}",
                    attachment_type=AttachmentType.JSON,
                    extension=".html"
                )
            except (JSONDecodeError, TypeError):
                allure.attach(
                    body=response.text.encode("utf8"),
                    name=f"Response text {response.status_code}",
                    attachment_type=AttachmentType.TEXT,
                    extension=".txt")
            # allure.attach(
            #     body=json.dumps(response.headers.items(), indent=4).encode("utf8"),
            #     name=f"Response headers {response.status_code}",
            #     attachment_type=AttachmentType.JSON,
            #     extension=".json"
            # )
        return response

    return wrapper

def attach_sql(cursor, statement, parameters, context):
    """Функция для логирования SQL-запросов в Allure"""
    allure.attach(
        body=statement,
        name="SQL Query",
        attachment_type=AttachmentType.TEXT,
        extension=".sql"
    )
    if parameters:
        allure.attach(
            body=str(parameters),
            name="SQL Parameters",
            attachment_type=AttachmentType.TEXT,
            extension=".txt"
        )