from http.client import HTTPException
import dataclasses
import json
import math
import re
import sys
import string
import random
import builtins
import inspect
import traceback
import asyncio
from functools import wraps
from typing import Any
from datetime import datetime
from importlib import import_module

import js
import pyodide


class UpgradedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, datetime):
            return o.strftime(__CONFIG__['default_datetime_format'])
        return super().default(o)


log = js.console
NONE_TYPE = type(None)
__CONFIG__ = {
    'debug': False,
    'style_head': True,
    'api_url': '/',
    'default_datetime_format': '%Y-%m-%dT%H:%M:%S.%f%Z',
    'modules': [],
}


def merge_configs():
    __CONFIG__.update(js.pyweb.__CONFIG__.to_py())
    js.pyweb.__CONFIG__ = pyodide.to_js(__CONFIG__, dict_converter=js.Object.fromEntries)


if pyodide.ffi.IN_BROWSER:
    merge_configs()


_current_render: list['Renderer', ...] = []
_current_rerender: list['Renderer', ...] = []
_current__lifecycle_method: dict[str, dict[int, 'Tag']] = {}
_current: dict[str, Any] = {
    'render': _current_render,
    'rerender': _current_rerender,
    '_lifecycle_method': _current__lifecycle_method,
}


def _debugger(error=None):
    log.warn(traceback.format_exc())
    js._locals = pyodide.to_js(inspect.currentframe().f_back.f_locals, dict_converter=js.Object.fromEntries)
    js._DEBUGGER(error)


def log10_ceil(num):
    return math.ceil(math.log10(num or 1)) or 1


_w = string.ascii_letters + string.digits + '_'


def get_random_name(length=6):
    return ''.join(
        random.choice(_w)
        for _ in range(length)
    )


def to_kebab_case(name: str):
    """
    parsing name of tag to html-compatible or name of property to css-compatible
    >>> class __pyweb__(Tag): ...  # <pyweb></pyweb>
    >>> class myTagName(Tag): ...  # <my-tag-name/>
    >>> style(font_size='20px')  # font-size: 20px
    >>> style(backgroundColor='red')  # background-color: red
    """
    return re.sub(
        r'([A-Z])',
        lambda m: '-' + m.group(1).lower(),
        re.sub('[_ ]', '-', name)
    ).strip('-')


class const_attribute(property):
    def __set__(self, instance, value):
        if self.__get__(instance) is None:
            super().__set__(instance, value)
        else:
            raise AttributeError


async def request(url, method='GET', body=None, headers=None, **opts):
    if body is not None:
        body = json.dumps(body, cls=UpgradedJSONEncoder)

    if headers is None:
        headers = {}

    headers.update({
        'mode': 'no-cors',
        'Content-Type': 'application/json',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Origin': '*',
    })

    response = await pyodide.http.pyfetch(
        __CONFIG__['api_url'] + 'api/' + url, method=method, body=body, headers=headers, **opts
    )

    if int(response.status) >= 400:
        raise HTTPException(response.status)

    if method == 'GET' or opts.get('to_json'):
        response = await response.json()
    else:
        response = await response.string()

    return response


if not pyodide.ffi.IN_BROWSER:
    import requests

    async def request(url, method='GET', body=None, headers=None, **opts):
        if body is not None:
            body = json.dumps(body, cls=UpgradedJSONEncoder)

        if headers is None:
            headers = {}

        # TODO: check opts argument compatibility

        response = requests.request(
            method, __CONFIG__['api_url'] + 'api/' + url, data=body, headers=headers,
        )

        if int(response.status_code) >= 400:
            raise HTTPException(response.status_code)

        if method == 'GET' or opts.get('to_json'):
            response = response.json()
        else:
            response = response.text

        return response


def js_func(once=False):
    if once:
        create_proxy = pyodide.create_once_callable
    else:
        create_proxy = pyodide.create_proxy

    return create_proxy


def ensure_sync(to_await):
    if asyncio.iscoroutine(to_await):
        return asyncio.get_event_loop().run_until_complete(to_await)
    return to_await


def force_sync(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        return ensure_sync(function(*args, **kwargs))
    return wrapper


delay = js.delay


@ensure_sync
async def sleep(s):
    return await js.delay(s * 1000)


class Locker:
    __slots__ = ('name', 'locked')

    def __init__(self, name='Lock'):
        self.name = name
        self.locked = False

    def __enter__(self):
        self.locked = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.locked = False

    def __bool__(self):
        return self.locked

    def __str__(self):
        return f'Locker<{self.name}>({self.locked})'


def cached_import(module_path, class_name=None, package=None):
    if module_path.startswith('.') and package is None:
        package = '__pyweb_root__'

    modules = sys.modules
    if module_path not in modules or (
        # Module is not fully initialized.
        getattr(modules[module_path], '__spec__', None) is not None
        and getattr(modules[module_path].__spec__, '_initializing', False) is True
    ):
        if pyodide.ffi.IN_BROWSER:
            js.pyweb._loadLocalFileSync(module_path.lstrip('.'))
        import_module(module_path, package)

    if module_path.startswith('.') and package == '__pyweb_root__':
        module_path = f'{package}{module_path}'

    if class_name:
        return getattr(modules[module_path], class_name)
    else:
        return modules[module_path]


def import_cls(import_string):
    module_path, class_name = import_string.rsplit('.', 1)
    return cached_import(f'.{module_path}', class_name)


def lazy_import_cls(cls):
    if isinstance(cls, str):
        return import_cls(cls)
    return cls


_all_globals = builtins.__dict__
_globals = {}
_allowed_globals = (
    '__name__', 'abs', 'all', 'any', 'ascii', 'bin', 'breakpoint', 'callable', 'chr', 'delattr', 'dir', 'divmod',
    'format', 'getattr', 'hasattr', 'hash', 'hex', 'id', 'input', 'isinstance', 'issubclass', 'iter', 'len', 'max',
    'min', 'next', 'oct', 'ord', 'pow', 'print', 'repr', 'round', 'setattr', 'sorted', 'sum', 'vars', 'None',
    'Ellipsis', 'False', 'True', 'bool', 'memoryview', 'bytearray', 'bytes', 'complex', 'dict', 'enumerate', 'filter',
    'float', 'frozenset', 'int', 'list', 'map', 'object', 'range', 'reversed', 'set', 'slice', 'str', 'tuple', 'type',
    'zip',
)
for _key, _value in _all_globals.items():
    if _key in _allowed_globals:
        _globals[_key] = _value


def safe_eval(code, _locals=None):
    if _locals is None:
        _locals = {}

    return eval(code, _globals, _locals)


__all__ = [
    'log', 'NONE_TYPE', '__CONFIG__', '_current', '_debugger', 'get_random_name', 'to_kebab_case',
    'const_attribute', 'js_func', 'ensure_sync', 'force_sync', 'delay', 'sleep', 'safe_eval',
    'cached_import', 'import_cls', 'lazy_import_cls',
]
