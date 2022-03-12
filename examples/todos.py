from __future__ import annotations

# [PYWEB IGNORE START]
from pyweb import Tag, Children, mount, attr, state, on, style, div, p, _input, button, span
# [PYWEB IGNORE END]

_p = p()


class TodoList(Tag, name='ul'):
    class AddTodo(div, name='form'):
        input = _input()
        button = button('+', type='submit')

        parent: TodoList

        @on
        def submit(self, event):
            event.preventDefault()
            self.parent.add_todo(self.input.value)
            self.input.clear()

    ####

    class Todo(Tag, name='li', content_tag=_p):
        completed: bool = attr()

        parent: TodoList

        remove = span('×')

        @on('click')
        def toggle(self, event):
            self.completed = not self.completed
            self.parent.recalculate_completed()

        @remove.on('click')
        def delete(self, event):
            self.parent.todos.remove(self)

    ####

    count_completed: int = state(0)

    style = style(styles={
        'zoom': 3,
        'padding': '0 24px',
        'form': {
            'display': 'flex',
            'flex-flow': 'row nowrap',
            'align-items': 'center',
            'input': {
                'border': 'none',
                'outline': 'none',
                'border-radius': '.5rem',
                'padding': '.5rem',
                'height': '1.5rem',
                'flex': '0 1 calc(80% - 0.5rem)',
                'margin-right': '.5rem',
            },
            'button': {
                'cursor': 'pointer',
                'height': '2.5rem',
                'width': '2.5rem',
                'border-radius': '.5rem',
                'font-size': '1.25rem',
                'font-weight': 500,
                'border': 'none',
                'outline': 'none',
                'color': '#dddddd',
                'background-color': '#4a8cce',
            },
        },
        'li': {
            'display': 'flex',
            'flex-flow': 'row nowrap',
            'align-items': 'center',
            'user-select': 'none',
            'span': {
                'cursor': 'pointer',
                'margin-right': '1rem',
                '&:hover': {
                    'color': '#f05454',
                }
            },
            '&[completed]': {
                'p:before': {
                    'top': '10px',
                    'height': '2px',
                    'transform': 'scaleX(1)',
                },
            },
            'p': {
                'cursor': 'pointer',
                'position': 'relative',
                'margin-right': '1rem',
                '&:before': {
                    'position': 'absolute',
                    'z-index': 5,
                    'content': '',
                    'top': '9px',
                    'left': 0,
                    'width': '100%',
                    'height': '4px',
                    'background-color': '#4a8cce',
                    'transform': 'scaleX(0)',
                    'transform-origin': 'left',
                    'transition': 'all .2s ease-in-out',
                },
                '&:hover:before': {
                    'top': '9px',
                    'height': '4px',
                    'transform': 'scaleX(1)',
                },
            },
        },
    })

    add = AddTodo()

    todos = Children([
        Todo('Create Todo List', completed=True),
    ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recalculate_completed()

    def content(self):
        return f'Completed: {self.count_completed}/{len(self.todos)}'

    def add_todo(self, todo):
        if not todo:
            return

        self.todos.append(self.Todo(todo))

    def recalculate_completed(self):
        self.count_completed = len([todo for todo in self.todos if todo.completed])


mount(
    TodoList(),
    '#pyweb',
)