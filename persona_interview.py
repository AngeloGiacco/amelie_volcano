import streamlit as st
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

chat_history_key = "chat_history"
if chat_history_key not in st.session_state:
    st.session_state[chat_history_key] = []
from langchain_core.prompts import ChatPromptTemplate


class Response(BaseModel):
    response: str = Field(
        description="your response. be friendly and engaging and make sure to follow your persona"
    )


# Defining the function as per your request
def get_start(persona: str):
    chat = ChatOpenAI(api_key=st.secrets["OpenAI_API_KEY"]).with_structured_output(
        Response
    )
    system = """
    You are to be controlled by a certain persona in an interview with a market researcher. 
    In the user prompt we will reveal what that persona is. 
    Say hi and explain that you are looking forward to the interview. 
    We're going to interview you about starting a non-profit organisation that advocates for increased volcano risk awareness.
    Please be engaged and willing to respond. Help us to understand how volcanic risk affects you in your industry.
    """

    prompt = ChatPromptTemplate.from_messages(
        [("system", system), ("human", "{persona}")],
    )

    chain = prompt | chat
    result = chain.invoke({"persona": persona})
    return result.response


def continue_conversation():
    response = st.session_state.user_input
    st.session_state[chat_history_key].append(("user", response))
    llm_response = get_response()
    print(llm_response)
    st.session_state[chat_history_key].append(("assistant", llm_response))


def get_response():
    persona = st.session_state.persona

    chat = ChatOpenAI(api_key=st.secrets["OpenAI_API_KEY"]).with_structured_output(
        Response
    )
    prompt = ChatPromptTemplate.from_messages(
        st.session_state[chat_history_key],
    )

    chain = prompt | chat
    result = chain.invoke({"persona": persona})
    return result.response


st.title("Hi i love you Am <333")


def start_interview():
    persona = st.session_state.persona
    system_prompt = f"""You have the persona of {persona}. You are being interviewed by a market researcher. We're going to interview you about starting a non-profit organisation that advocates for increased volcano risk awareness.
    Please be engaged and willing to respond. Help us to understand how volcanic risk affects you in your industry."""
    st.session_state[chat_history_key] = [("system", system_prompt)]
    st.session_state[chat_history_key].append(("assistant", get_start(persona)))


with st.form("my_form"):
    # Define the available languages and levels
    with st.sidebar:
        topic = st.text_input("enter the persona", key="persona")

        submit = st.form_submit_button("Start interview!", on_click=start_interview)


for user, text in st.session_state[chat_history_key]:
    if user == "system":
        with st.chat_message("assistant"):
            st.markdown(
                f"All interactions with the LLM will be dictated by the persona. Here is the description of the persona: {text}"
            )
    else:
        with st.chat_message(user):
            st.markdown(text, unsafe_allow_html=True)

if len(st.session_state[chat_history_key]) > 0:
    with st.form(key="user_input_form"):
        user_input = st.text_input("Your message:", key="user_input")
        submit_button = st.form_submit_button(label="Send")

        if submit_button and user_input.strip():
            continue_conversation()
            st.rerun()
