from fasthtml.common import (AX, Button, Card, CheckboxX, Div, Footer, Form, Group,
                             Hidden, Input, Li, Titled, Ul, fast_app, Fieldset, Small,
                             fill_dataclass, fill_form, serve)
from dataclasses import dataclass, field
from polylist.common import mk_list_item_input
from polylist.emoji_from_todo import get_emoji_for_todo

import randomname
import asyncio


id_curr = 'current-todo'
list_ul = 'list-ul'
def tid(id): return f'todo-{id}'


@dataclass
class ListItem():
    list_name: str; title: str; done: bool = False; emojies: str = ""
    def __ft__(self):
        raise NotImplementedError()
        checkbox = CheckboxX(id=f'done-{self.id}', checked=self.done, 
                     hx_post=f'{self.list_name}/toggle/{self.id}', 
                     hx_target=f'#{tid(self.id)}',
                     hx_swap='outerHTML')

        show = Div(self.title, 
               hx_get=f'{self.list_name}/edit/{self.id}', 
               hx_trigger='click',
               hx_target='this',
               hx_swap='outerHTML',
               style="display: inline-block; margin-left: 10px;")
    
        return Li(Fieldset(checkbox,
                      show, 
                     id=tid(self.id)))
    
    async def update_emojies(self):
        await get_emoji_for_todo(self.title)


@dataclass
class PolyList():
    name: str
    items: list[ListItem] = field(default_factory=list)
    

    def __ft__(self):
        return self.as_card()

    def add_item_form(self):
        return Form(Group(mk_list_item_input(), Button("Add")),
               hx_post=f"/{self.name}", target_id=list_ul, hx_swap="beforeend")
        
    @classmethod
    def get_by_name(cls, name):
        if name == "":
            name = randomname.get_name()
            poly_list = PolyList(name=name)
            [poly_list.add_item(title, done) for title, done in WELCOME_NOTE]
            return poly_list
        try:
            poly_list = lists[name]
        except KeyError:
            if not name:
                name = randomname.get_name()
            poly_list = PolyList(name)

            lists[name] = poly_list
        return poly_list

    def render_item(self, id: int):
        item = self.items[id]
        checkbox = CheckboxX(id=f'done-{id}', checked=item.done, 
                     hx_post=f'{self.name}/toggle/{id}', 
                     hx_target=f'#todo-{id}',
                     hx_swap='outerHTML')

        show = Div(
            item.title, 
            hx_get=f'{self.name}/edit/{id}', 
            hx_trigger='click',
            hx_target='this',
            hx_swap='outerHTML',
            style="display: inline-block; margin-left: 10px;",
            )
    
        return Li(Fieldset(checkbox,
                      show,
                      Small(item.emojies, style="margin-left: 10px;"),
                     id=f"todo-{id}"))

    def as_ul(self):
        return Ul(*[self.render_item(id) for id in range(len(self.items))], id=list_ul)

    def as_card(self):
        return Card(self.as_ul(), footer=self.add_item_form())
    
    def get_item_by_id(self, id):
        return self.items[id]
    
    def add_item(self, title: str, done: bool = False):
        item = ListItem(list_name=self.name, title=title, done=done)
        self.items.append(item)
        return item, len(self.items) - 1
    
    def update_item(self, id: int, title: str):
        item = self.items[id]
        item.title = title
        self.schedule_updating_emojies(id)
        return item
    
    async def update_emojies(self, id: int):
        item = self.items[id]
        item.emojies = await get_emoji_for_todo(item.title)
        return item
    
    def schedule_updating_emojies(self, id: int):
        asyncio.get_event_loop().create_task(self.update_emojies(id))

    def delete_item(self, id: int):
        item = self.items.pop(id)
        return item

    def toggle_item(self, id: int):
        item = self.items[id]
        item.done = not item.done
        return item


WELCOME_NOTE = [
    ("Welcome to PolyList!", True),
    ("Click on a todo item text to edit it.", False),
    ("Click on the checkbox to mark it as done.", False),
    ("Click on the 'Add' button to add a new todo item.", False),
    ("Click on the '+' button to create a new list.", False),
    ("This is beta application. All notes are currently public.", False),
]

lists = {
    
    "": PolyList(name="Welcome"),
}
