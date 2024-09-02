from langchain_community.llms.fake import FakeListLLM
from polylist.emoji_from_todo import get_emoji_for_todo, create_emoji_prompt
import pytest


def test_create_emoji_prompt():
    prompt = create_emoji_prompt()
    assert prompt.template == "Suggest a set of one or more emoji that describe the provided item, respond with emoji only: /n {todo}"
    assert prompt.input_variables == ["todo"]

@pytest.mark.asyncio
async def test_get_emoji_for_todo():
    # Create a FakeListLLM with predetermined responses
    fake_llm = FakeListLLM(responses=["🛒"])
    
    # Test the function
    result = await get_emoji_for_todo("Buy groceries", fake_llm)
    assert result == "🛒"
