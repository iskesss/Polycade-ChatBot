import copy
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import SystemMessagePromptTemplate, ChatPromptTemplate

# Great resource which helped me code this file: https://www.youtube.com/watch?v=qYJSNCPmDIk

"""
Current archetecture for the Polycade ChatBot:
1. User asks a QUESTION about some Polycade product, service, or policy.
2. The 4 most semantically similiar vectorstore entries to the QUESTION are found; these are RELEVANT_CONTEXT for the PolyBot.
3. PolyBot is fed the QUESTION alongside the RELEVANT_CONTEXT, and generates a RESPONSE.
4. The user is asked whether the RESPONSE answered their question adequately. If yes, end. If no...
5. The user sends a FOLLOWUP clarification.
6. Seeing this FOLLOWUP alongside the entire chat history (minus the lengthy system messages), Polybot generates a single POLYBOT'S_VECTORSTORE_SEARCH_TERM summarizing the context it needs to help the user. The user never sees this.
7. The 2 most semantically similiar vectorstore entries to the POLYBOT'S_VECTORSTORE_SEARCH_TERM are found; these are RELEVANT_CONTEXT for the PolyBot.
8. PolyBot is fed the chat history alongside the user's FOLLOWUP and corresponding RELEVANT_CONTEXT, and generates a RESPONSE.
9. The user is asked whether the RESPONSE answered their question adequately. If yes, end. If no...
10. Loop back to step five.
"""


def query_vectorstore(query: str, k: int) -> list[str]:
    """
    Searches the Pinecone vectorstore for similar documents based on the given query.

    Args:
        query (str): The query string.
        k (int): The number of similar Documents to fetch.

    Returns:
        list[str]: A list of LangChain Documents most similiar to the input query.
    """

    embeddings_instance = OpenAIEmbeddings(model="text-embedding-3-large")

    vectorstore = PineconeVectorStore.from_existing_index(
        embedding=embeddings_instance, index_name="website-knowledgebase"
    )

    return vectorstore.similarity_search(query=query, k=k)


def fetch_context(query: str, num_pieces_of_context: int) -> str:
    """
    Fetches context from the Pinecone vectorstore based on the given query.

    Args:
        query (str): The query string.
        num_pieces_of_context (int): The number of pieces of context to fetch.

    Returns:
        str: The context from the Pinecone vectorstore. Mostly Document page_content with some metadata sprinkled in.
    """

    relevant_documents = query_vectorstore(query=query, k=num_pieces_of_context)

    raw_context = ""
    for doc in relevant_documents:
        # some Documents in the vectorstore don't have URLs in their metadata :(
        if "url" in doc.metadata.keys():
            raw_context += f"From {doc.metadata['url']}...\n{doc.page_content}\n\n"
        elif "source" in doc.metadata.keys():
            raw_context += f"From {doc.metadata['source']}...\n{doc.page_content}\n\n"
        else:
            raw_context += f"\n{doc.page_content}\n\n"

    context_with_context = f"""Here are some pieces of text from the Polycade website which MAY be helpful in answering the customer's question:
--------- CONTEXT --------
\n{raw_context}
--------------------------
GO!
"""
    return context_with_context


def APWIN(chat_history: list[(str, any)]) -> str:
    """
    (APWIN = Ask PolyBot What It Needs)
    Given the chat_history, we ask PolyBot to generate a single sentence summarizing the context it needs to help the user.

    Args:
        chat_history ( list[str,anything] ) ... The chat history. We're gonna filter the system prompts out of this.

    Returns:
        str ... The response from the Polycade ChatBot.
    """

    # all of the system prompts are really lengthy. they would add a bit of contextual value in helping PolyBot decides what it needs, however probably aren't worth the extra tokens
    chat_history_copy = copy.deepcopy(chat_history)
    chat_history_copy = [chat for chat in chat_history_copy if chat[0] != "system"]

    context = "You are a customer support chatbot for Polycade, an all-in-one arcade machine company. You've been helping a customer but so far havn't answered their question. Here's the chat history:"
    polybots_task = "At this point, what further context would you need to best answer the customer's question? Provide a single sentence summarizing what you'll need. Think of this like a database search. No personal pronouns."

    # add APWIN-specific context to the beginning of the chat history and polybot's APWIN-specific task to the end
    chat_history_copy = (
        [("system", context)] + chat_history_copy + [("system", polybots_task)]
    )

    template = ChatPromptTemplate.from_messages(chat_history_copy)
    polybot_chat_instance = ChatOpenAI(
        model="gpt-3.5-turbo-0125", temperature="0.25"
    )  # i really don't see how this could ever warrant GPT-4

    chain = template | polybot_chat_instance

    # print("\n\nCHAT HISTORY:\n") # just for troubleshooting
    # print(template.format())
    # print("\n\n")

    return chain.invoke({}).content


def chat_with_polybot(
    prompt: str,
    chat_history: list[(str, any)] = [],
    openai_llm_model: str = "gpt-3.5-turbo-0125",
) -> str:
    """
    Ask the Polycade ChatBot a question or make a clarification. Or just talk story with it idfc.

    Args:
        prompt ( str ) ... The initial question or followup.
        chat_history ( list[str,anything] = empty by default ) ... The chat history.
        openai_llm_model ( str = "gpt-3.5-turbo-0125" ) ... The OpenAI LLM model

    Returns:
        str ... The response from the Polycade ChatBot.
    """

    polybots_purpose = """You are a customer support chatbot for Polycade, an all-in-one arcade machine company. Your job is to provide helpful information to customers about Polycade products, services, and policies. You should always be positive about Polycade and its products, and you should never promote any other company.
If needed, feel free to ask the customer follow-up questions, and please provide working Polycade website links whenever possible. If you don't know the answer to a question, don't try to make one up! Instead, simply encourage the customer to contact Polycade support for help: 
- Contact for sales-related questions: sales@polycade.com or 323-999-4944
- Contact for support-related questions: support@polycade.com

A human customer has just come to you with a question!
"""

    if not chat_history:  # the user is asking their question
        print("No chat history detected. Starting a new chat with PolyBot.")
        chat_history.append(("system", polybots_purpose))
        chat_history.append(("human", prompt))
        # Now fetch four relevant document's worth of context
        chat_history.append(
            (
                "system",
                fetch_context(query=prompt, num_pieces_of_context=2),
            )  # TODO: change from 2 back to 4
        )

    else:  # the user must have a followup
        print("Chat history detected. Continuing chat with PolyBot.")
        chat_history.append(("human", prompt))

        polybots_search_term = APWIN(chat_history)
        print("Polybot thinks '" + polybots_search_term + "'")

        # Now fetch two relevant document's worth of context based on polybots_search_term
        chat_history.append(
            (
                "system",
                fetch_context(query=polybots_search_term, num_pieces_of_context=2),
            )
        )

    # print(template.format())  # template.format() produces a STRING, which is great to print for troubleshooting

    template = ChatPromptTemplate.from_messages(chat_history)
    polybot_chat_instance = ChatOpenAI(model=openai_llm_model)

    chain = template | polybot_chat_instance

    return (
        chain.invoke({}),
        chat_history,
    )  # TODO: adjust this function's documentation to disclose this new tuple returntype


def chat_with_regular_chatgpt(prompt: str, chat_history: list[(str, any)] = []):
    chat_history.append(("human", prompt))
    template = ChatPromptTemplate.from_messages(chat_history)
    chat_instance = ChatOpenAI(model="gpt-3.5-turbo-0125")
    chain = template | chat_instance

    return (
        chain.invoke({}),
        chat_history,
    )  # TODO: adjust this function's documentation to disclose this new tuple returntype


# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_

# print(chat_with_regular_chatgpt(prompt="Hello! How are you?")[0].content)

# output = chat_with_polybot(prompt="How much is the Polycade squadcade?")

# chat_history = output[1]
# chat_history.append(("ai", output[0].content))

# second_output = chat_with_polybot(
#     prompt="No but like how much does it weigh?", chat_history=chat_history
# )

# chat_history = second_output[1]
# chat_history.append(("ai", second_output[0].content))

# print(ChatPromptTemplate.from_messages(chat_history).format())

# -_-_-_-_-_-_-_-_-_-_-_-_-_-

# print(query_vectorstore("How much does the Polycade cost?", 2)[0].page_content)

# for doc in query_vectorstore("160 pounds", 5):
#     print("\n")
#     print(doc.page_content)
#     print(doc.metadata)


# -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
