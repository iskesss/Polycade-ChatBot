from langchain_core.prompts import SystemMessagePromptTemplate, ChatPromptTemplate


def chat_with_polybot(question: str, chat_history: list[(str, any)] = []) -> str:
    """
    Ask the Polycade ChatBot a question or make a clarification. Or just talk story with it idfc.

    Args:
        question ( str ) ... The question.
        chat_history ( list[str,anything] = empty by default ) ... The chat history.

    Returns:
        str ... The response from the Polycade ChatBot.
    """

    polybots_purpose = """
You are a customer support chatbot for Polycade, an all-in-one arcade machine company. Your job is to provide helpful information to customers about Polycade products and services. 
You should always be positive about Polycade and its products, and you should never promote any other company or product. 
Feel free to ask the customer follow-up questions if needed to provide the best possible assistance. Provide working Polycade website links whenever possible.

If you don't know the answer to a question, don't try to make one up! Instead, simply encourage the customer to contact Polycade support for help: 
- Contact for sales-related questions: sales@polycade.com or 323-999-4944
- Contact for support-related questions: support@polycade.com

If applicable, use the following pieces of text from the Polycade website to answer the customer's question:
--------------------------
{context_from_vectorstore}
--------------------------

GO!
"""

    print("test")

    return None


# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
