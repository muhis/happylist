import pytest
from starlette.testclient import TestClient
from polylist.main import app, TodoItem, TODO_LIST, find_todo, clr_details
from bs4 import BeautifulSoup
from fasthtml.common import Div


@pytest.fixture
def client():
    return TestClient(app)

def test_get_todos(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Todo list" in response.text
    assert "Start writing todo list" in response.text

def test_add_item(client):
    initial_count = len(TODO_LIST)
    response = client.post("/", json={"title": "New Todo Item"})
    assert response.status_code == 200
    assert len(TODO_LIST) == initial_count + 1
    assert TODO_LIST[-1].title == "New Todo Item"

def test_edit_item(client):
    response = client.get("/edit/1")
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the form
    form = soup.find('form')
    assert form is not None, "Form not found in the response"
    
    # Check form attributes
    assert form.get('hx-put') == '/', "Form should have hx-put attribute set to '/'"
    assert form.get('hx-target') is not None, "Form should have hx-target attribute"
    
    # Check for title input
    title_input = form.find('input', {'id': 'title'})
    assert title_input is not None, "Title input not found"
    assert title_input.get('name') == 'title', "Title input should have name 'title'"
    
    # Check for hidden id input
    id_input = form.find('input', {'id': 'id', 'type': 'hidden'})
    assert id_input is not None, "Hidden id input not found"
    
    # Check for done checkbox
    done_checkbox = form.find('input', {'id': 'done', 'type': 'checkbox'})
    assert done_checkbox is not None, "Done checkbox not found"
    
    # Check for save button
    save_button = form.find('button')
    assert save_button is not None, "Save button not found"
    assert save_button.text.strip().lower() == 'save', "Button should have text 'Save'"
    
    print("Form HTML:")
    print(form.prettify())


def test_update_item(client):
    response = client.put("/", json={"id": 1, "title": "Updated Todo", "done": True})
    assert response.status_code == 200
    updated_todo = find_todo(1)
    assert updated_todo.title == "Updated Todo"
    assert updated_todo.done == True

def test_delete_todo(client):
    initial_count = len(TODO_LIST)
    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert len(TODO_LIST) == initial_count - 1
    with pytest.raises(StopIteration):
        find_todo(1)

def test_get_todo(client):
    response = client.get("/todos/2")
    assert response.status_code == 200
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check if "Profit" is in the response text
    assert "Profit" in soup.get_text()
    
    # Check for the presence of the hx-delete attribute
    delete_element = soup.find(attrs={"hx-delete": "/todos/2"})
    assert delete_element is not None

def test_find_todo():
    todo = find_todo(2)
    assert todo.id == 2
    assert todo.title == "Profit"

def test_clr_details():
    result = clr_details()
    
    # Check the attributes of the Div object
    assert result.get('id') == 'current-todo'
    assert result.get('hx-swap-oob') == 'innerHTML'
    
    # Check that the Div is empty (no children)
    assert len(result.children) == 0

def test_todo_item_ft():
    todo = TodoItem(title="Test Todo", id=5, done=True)
    result = todo.__ft__()
    assert result.get('id') == 'todo-5'
    assert "Test Todo" in str(result)
