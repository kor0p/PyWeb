from pyweb import Tag, mount, state, on
from pyweb.tags import div


class IncrementButton(Tag, name='button'):
    title = state('')
    count = state(0)

    @on
    def click(self, event):
        self.count += 1

    def content(self):
        return f'{self.title} | Count: {self.count}'


class View(Tag, name='view'):
    children = [
        IncrementButton(title='Outer'),
        div(id='inner-root'),
    ]


mount(View(), '#root')
mount(IncrementButton(title='Inner'), '#inner-root')
