import streamlit as st
from core import chat_with_polybot, chat_with_regular_chatgpt
from streamlit_chat import message

with open("styles.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)


st.title("PolyBot")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# display messages from history on app rerun
for message in st.session_state.chat_history:
    if message[0] == "ai":
        with st.chat_message(message[0], avatar="polycade-icon.jpg"):
            st.markdown(message[1])
    elif message[0] == "human":
        with st.chat_message(message[0], avatar="🕹️"):
            st.markdown(message[1])
    else:
        print("Filtered System Message")


user_query = st.chat_input(placeholder="Ask me something about Polycade!")
if user_query:
    with st.chat_message("human", avatar="🕹️"):
        st.markdown(user_query)

    with st.spinner("Hmm..."):
        polybot_output = chat_with_polybot(
            prompt=user_query, chat_history=st.session_state["chat_history"]
        )
        updated_chat_history = polybot_output[1]
        updated_chat_history.append(("ai", polybot_output[0].content))
        st.session_state["chat_history"] = updated_chat_history

    with st.chat_message("ai", avatar="polycade-icon.jpg"):
        st.markdown(polybot_output[0].content)
