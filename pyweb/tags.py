from typing import Any, Optional

import js

from .framework import Tag
from .attrs import attr, state, html_attr
from .children import Children
from .utils import get_random_name, __CONFIG__


AUTO_ID = object()


class html_tag(Tag, _root=True, content_tag=None):
    id = attr(type=str)
    _class = attr(type=str)

    def __set_ref__(self, parent, ref):
        super().__set_ref__(parent, ref)
        if type(self).id is html_tag.id and (
            self.id is AUTO_ID or (__CONFIG__['inputs_auto_id'] and self.id is None)
        ):
            self.id = f'{ref.name or get_random_name(5)}-{get_random_name(2)}'


def by__input_id(input_tag, value):
    if value is None:
        return False
    return input_tag.id.rsplit('-', 1)[0]


class div(html_tag, name='div', content_tag=None):
    pass


class hr(html_tag, name='hr'):
    pass


class a(html_tag, name='a'):
    href = attr(type=str)


class p(html_tag, name='p'):
    pass


class ul(html_tag, name='ul'):
    pass


class li(html_tag, name='li'):
    pass


class span(html_tag, name='span'):
    pass


class table(html_tag, name='table'):
    pass


class thead(html_tag, name='thead'):
    pass


class tbody(html_tag, name='tbody'):
    pass


class tr(html_tag, name='tr'):
    pass


class th(html_tag, name='th'):
    pass


class td(html_tag, name='td'):
    pass


class label(html_tag, name='label'):
    _for = attr(type=str)

    def __set_ref__(self, parent, ref):
        super().__set_ref__(parent, ref)
        if parent and isinstance(self._for, Tag):
            self._for = self._for._ref.__get__(parent).id


class h1(html_tag, name='h1'):
    pass


class h2(html_tag, name='h2'):
    pass


class h3(html_tag, name='h3'):
    pass


class h4(html_tag, name='h4'):
    pass


class h5(html_tag, name='h5'):
    pass


class h6(html_tag, name='h6'):
    pass


class _input(html_tag, name='input'):
    type = attr(
        'text',
        enum=(
            'button', 'checkbox', 'color', 'date', 'datetime-local', 'email', 'file', 'hidden', 'image', 'month',
            'number', 'password', 'radio', 'range', 'reset', 'search', 'submit', 'tel', 'text', 'time', 'url', 'week',
        ),
    )
    hidden = attr(False)
    value = html_attr('', model='input')

    def clear(self):
        self.value = ''


class textarea(html_tag, name='textarea'):
    value = html_attr('', model='change')

    def clear(self):
        self.value = ''


class button(html_tag, name='button'):
    type = attr('button', type=str, enum=('submit', 'reset', 'button'))


class option(html_tag, name='option'):
    value = html_attr()
    label = html_attr('')
    defaultSelected = html_attr(False)
    selected = html_attr(False)


class select(html_tag, name='select'):
    value = html_attr(model='change')

    options = Children()

    children = [
        options,
    ]

    def select(self, value):
        self.value = value

    @classmethod
    def with_items(cls, items: dict[str, Any], **kwargs):
        return cls(options=[
            option(label=label_, value=value)
            for value, label_ in items.items()
        ], **kwargs)


class StandaloneTag(html_tag, _root=True):
    def __init__(self, *args, **kwargs):
        kwargs['_load_children'] = True
        super().__init__(*args, **kwargs)

    def __mount__(self, element, parent: Tag, index=None):
        # too many copy-paste?
        self.parent = parent
        self.mount_parent = element
        self.pre_mount()

    def clone(self, parent=None):
        return self

    def as_child(self, parent: Optional[Tag], exists_ok=False):
        return super().as_child(parent, True)


class Head(StandaloneTag, name='head', mount=js.document.head):
    title = state()

    def render(self):
        if self.title:
            js.document.title = self.title


Head = Head()


class Body(StandaloneTag, name='body', mount=js.document.body):
    pass


Body = Body()


# TODO: add all HTML tags


__all__ = [
    'html_tag', 'div', 'a', 'p', 'ul', 'li', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    '_input', 'textarea', 'button', 'option', 'select', 'Head',
]
