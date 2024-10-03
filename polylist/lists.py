from fasthtml.common import (AX, Button, Card, CheckboxX, Div, Footer, Form, Group, H4, Strong,
                             Hidden, Input, Li, Titled, Ul, fast_app, Fieldset, Small, Nav, A,
                             fill_dataclass, fill_form, serve)
from dataclasses import dataclass, field
from polylist.common import mk_list_item_input
from polylist.emoji_from_todo import get_emoji_for_todo

import randomname
import asyncio


id_curr = 'current-todo'
list_ul = 'list-ul'
def tid(id): return f'todo-{id}'


def make_list_nav_bar(list_name:str):
    return Nav(
        Ul(Li(H4(list_name))),
        Ul(
            Li(Button("Share 📤", onclick=f"reply_click('{list_name}')"))
        )
    )

@dataclass
class ListItem():
    list_name: str; title: str; done: bool = False; emojies: str = ""
    
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
               hx_post=f"/list/{self.name}", target_id=list_ul, hx_swap="beforeend")
        
    @classmethod
    def get_by_name(cls, name):
        return lists[name]
    
    @classmethod
    def new_welcome_note(cls):
        poly_list = cls.new()
        [poly_list.add_item(title, done, emojies) for title, done, emojies in WELCOME_NOTE]
        return poly_list

    @classmethod
    def new_about_note(cls):
        poly_list = cls.new()
        [poly_list.add_item(title, done, emojies) for title, done, emojies in ABOUT_NOTE]
        poly_list.add_item(title=f"{len(lists)} happy lists so far!", done=True, emojies="🤝🚀📋")
        return poly_list

    @classmethod
    def new(cls):
        """
        1. Create a new list
        2. Add a welcome note
        3. Return the name of the new list
        """
        name = randomname.get_name()
        while name in lists:
            name = randomname.get_name()

        new_list = cls(name=name)
        lists[name] = new_list

        return new_list

    def render_item(self, id: int):
        item = self.items[id]
        checkbox = CheckboxX(id=f'done-{id}', checked=item.done, 
                     hx_post=f'/list/{self.name}/toggle/{id}', 
                     hx_target=f'#todo-{id}',
                     hx_swap='outerHTML')

        show = Div(
            item.title, 
            hx_get=f'/list/{self.name}/edit/{id}', 
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
        header = make_list_nav_bar(self.name)
        return Card(self.as_ul(), header=header, footer=self.add_item_form())
    
    def get_item_by_id(self, id):
        return self.items[id]
    
    def add_item(self, title: str, done: bool = False, emojies: str = ""):
        item = ListItem(list_name=self.name, title=title, done=done, emojies=emojies)
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
    ("Welcome to HappyList!", True, "👋"),
    ("Make shopping fun!", False, "🛍️"),
    ("Tap to edit and see magic.", False, "✨"),
    ("Check off items as you go.", False, "✅"),
    ("Tap 'Add' for new treasures.", False, "➕"),
    ("HappyList adds emojis!", False, "⚡"),
    ("Tap '+' for a new quest.", False, "🎉"),
    ("This is test application!", False, "🚧"),
]



ABOUT_NOTE = [
    ("Made by Mohammed Salman", True, "👨‍💻"),
    ("Testing AI in life", True, "🧠"),
    ("Building small products", True, "💡"),
    ("linkedin.com/in/m-salman/", True, "🤝"),
    ("github.com/muhis/happylist", True, "🛠️"),
]


lists: dict[str, PolyList] = {

}
