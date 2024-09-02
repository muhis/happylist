from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseLanguageModel
from polylist import config

def create_emoji_prompt():
    """Create and return the PromptTemplate for emoji generation."""
    return PromptTemplate(
        input_variables=["todo"],
        template="Suggest a set of one or more emoji that describe the provided item in shopping list, respond with emoji only: /n {todo}"
    )

async def get_emoji_for_todo(todo: str, llm: BaseLanguageModel | None= None) -> str:
    """
    Get an emoji for a given todo item using the provided LLM chain.
    
    :param todo: The todo item text
    :param emoji_chain: An LLMChain instance to use for generating the emoji
    :return: An emoji string
    """
    if llm is None:
        llm = OpenAI(temperature=0)
    prompt = create_emoji_prompt()
    results = await llm.ainvoke(prompt.format_prompt(todo=todo).to_string()) or "❓"
    
    return results.strip()

# Usage example:
# emoji_chain = create_emoji_chain()
# emoji = get_emoji_for_todo("Buy groceries", emoji_chain)
