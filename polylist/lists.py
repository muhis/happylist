from fasthtml.common import (AX, Button, Card, CheckboxX, Div, Footer, Form, Group,
                             Hidden, Input, Li, Titled, Ul, fast_app, Fieldset,
                             fill_dataclass, fill_form, serve)
from dataclasses import dataclass
from polylist.common import mk_list_item_input

import randomname

id_curr = 'current-todo'
id_list = 'todo-list'
def tid(id): return f'todo-{id}'


@dataclass
class ListItem():
    title: str; id: int = -1; done: bool = False
    def __ft__(self):
        checkbox = CheckboxX(id=f'done-{self.id}', checked=self.done, 
                     hx_post=f'/toggle/{self.id}', 
                     hx_target=f'#{tid(self.id)}',
                     hx_swap='outerHTML')

        show = Div(self.title, 
               hx_get=f'/edit/{self.id}', 
               hx_trigger='click',
               hx_target='this',
               hx_swap='outerHTML',
               style="display: inline-block; margin-left: 10px;")
    
        return Li(Fieldset(checkbox,
                      show, 
                     id=tid(self.id)))
    


@dataclass
class PolyList():
    items: list[ListItem]
    name: str
    def __ft__(self):
        add = Form(Group(mk_list_item_input(), Button("Add")),
            hx_post="/", target_id=id_list, hx_swap="beforeend")
        cards = Card(Ul(*TODO_LIST, id=id_list),
                    footer=add)
        return Div(Titled(f"{self.name}")),


TODO_LIST = [ListItem(id=0, title="Start writing todo list", done=True),
             ListItem(id=1, title="???", done=False),
             ListItem(id=2, title="Profit", done=False)]