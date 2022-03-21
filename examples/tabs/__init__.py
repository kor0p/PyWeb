from pyweb import Tag, mount, state, __version__
from pyweb.style import style
from pyweb.tags import button, p, select, br, attr
from pyweb.tabs import tab, tab_title, tabs


class View(Tag, name='view'):
    class PyButton(button):
        color: str = state('gray')

        style = style(
            margin='8px',
            color='{color}',
        )

    count: int = attr(0)

    title: str = state()

    style = style(
        button=dict(
            backgroundColor='lightblue',
        )
    )

    button_inc = PyButton('+', color='red')
    button_dec = PyButton('–')

    @button_inc.on('click')
    def increment(self, event):
        self.count += 1

    @button_dec.on('click')
    def decrement(self, event):
        self.count -= 1

    def content(self):
        return (
            self.title,
            br,
            'Count: ', self.count
        )


class SelectView(Tag, name='div', content_tag='span'):
    selected: str = attr('1')

    items = {'0': 'first', '1': 'second', '2': 'third'}

    select = select.with_items(items, selected='1')

    @select.on
    def change(self, event):
        self.selected = event.target.value

    def content(self):
        return [
            p(lambda _: f'Key: {self.selected}'),
            p(lambda _: f'Value: {self.items[self.selected]}')
        ]


class LinkTabs(tabs):
    name = 'TEST'
    tabs_titles = {
        'tab_text': tab_title('Page 1'),
        'tab_buttons': tab_title('Page 2'),
        'tab_selector': tab_title('Page 3'),
    }

    tab_text = tab(
        f'''
        <p>PyWeb (version {__version__})</p>
        <p>
            A frontend framework for python, using <a href="https://pyodide.org/" target="_blank">pyodide</a>
            via <a href="https://webassembly.org/">WebAssembly</a>
        </p>
        <p>More examples:</p>
        <p><a href="https://pyweb.netlify.app/examples/" target="_blank">First try</a></p>
        <p><a href="https://pyweb.netlify.app/examples/tabs/" target="_blank">Tabs (this one)</a></p>
        <p><a href="https://pyweb.netlify.app/examples/todos/" target="_blank">Todo List</a></p>
        <p><a href="https://pyweb.netlify.app/examples/context-menu/" target="_blank">Context Menu</a></p>
        <p><a href="https://pyweb.netlify.app/examples/dynamic-url/" target="_blank">Dynamic URL</a></p>
        <p>Made by <a href="https://t.me/kor0p" target="_blank">© kor0p</a></p>
        <p>Source code of PyWeb: <a href="https://github.com/kor0p/PyWeb" target="_blank">GitHub</a></p>
        '''
    )
    tab_buttons = tab(
        View(title='PyWeb Test 2'),
    )
    tab_selector = tab(
        SelectView(),
    )


class test_tabs(Tag, name='test-tabs'):
    style = style(
        color='white',
        zoom=4,
        font_size='12px',
    )

    tabs = LinkTabs()


test = test_tabs()


mount(
    test,
    '#pyweb',
)