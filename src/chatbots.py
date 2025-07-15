from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage, HumanMessage
from langchain_core.runnables.passthrough import RunnablePick
from langchain_openai import ChatOpenAI

from src.prompts import *

MI_PROMPT_DICT = {
    0: {
        "prompt": MI_V5_PROMPT,
        "keylist": ["STAGE"],
    },
    1: {
        "prompt": MI_V6_PROMPT,
        "keylist": [
            "STAGE",
            "ONBOARDING_DATA",
            "SELF_REPORTS",
            "SESSION_NUMBER",
            "SESSION_NOTES",
            "SESSION_DATE",
        ],
    },
    2: {
        "prompt": MI_V7_PROMPT,
        "keylist": [
            "STAGE",
            "ONBOARDING_DATA",
            "SELF_REPORTS",
            "SESSION_NUMBER",
            "SESSION_NOTES",
            "SESSION_DATE",
        ],
    },
}

TTM_PROMPT_DICT = {
    0: {
        "prompt": TTM_V3_PROMPT,
    }
}


class MIChatbot:
    def __init__(self, openai_api_key: str, version=0, history=None):
        # Initialize ChatOpenAI model
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
            openai_api_key=openai_api_key,
        )

        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
        )

        # If history is provided, load it into memory
        if history:
            for msg in history:
                if msg["role"] == "user":
                    self.memory.chat_memory.add_message(
                        HumanMessage(content=msg["content"])
                    )
                elif msg["role"] == "assistant":
                    self.memory.chat_memory.add_message(
                        AIMessage(content=msg["content"])
                    )

        # Initialize prompt version and template
        self.prompt_version = version

        try:
            self.system_prompt = MI_PROMPT_DICT[version]["prompt"]
            self.prompt_keylist = MI_PROMPT_DICT[version]["keylist"]
        except:
            raise ValueError(
                f"Invalid version: {version}. Available versions: {list(MI_PROMPT_DICT.keys())}"
            )

        # Create the chat prompt template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

    def get_response(self, user_input: str, payload: dict) -> str:
        # Create chain
        chain = (
            RunnablePick(["input", "chat_history"] + self.prompt_keylist)
            | self.prompt
            | self.llm
        )

        response = chain.invoke(
            payload
            | {"input": user_input, "chat_history": self.memory.chat_memory.messages}
        )

        # Append the response to memory
        self.memory.chat_memory.add_message(HumanMessage(content=user_input))
        self.memory.chat_memory.add_message(AIMessage(content=response.content))

        return response.content

    def clear_memory(self):
        self.memory.clear()


class TTMChatbot:
    def __init__(self, openai_api_key, version=0, history=None):
        # Initialize the ChatOpenAI model
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
            openai_api_key=openai_api_key,
        )

        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
        )

        # If history is provided, load it into memory
        if history:
            for msg in history:
                if msg["role"] == "user":
                    self.memory.chat_memory.add_message(
                        HumanMessage(content=msg["content"])
                    )
                elif msg["role"] == "assistant":
                    self.memory.chat_memory.add_message(
                        AIMessage(content=msg["content"])
                    )

        # Initialize prompt
        self.prompt_version = version

        self.system_prompt = TTM_PROMPT_DICT[version]["prompt"]

        # Create the chat prompt template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

    def get_response(self, user_input: str) -> str:
        # Create the chain
        chain = self.prompt | self.llm

        # Get response
        response = chain.invoke(
            {"input": user_input, "chat_history": self.memory.chat_memory.messages}
        )

        # Update memory
        self.memory.chat_memory.add_message(HumanMessage(content=user_input))
        self.memory.chat_memory.add_message(AIMessage(content=response.content))

        return response.content

    def clear_memory(self):
        """Clear the conversation memory"""
        self.memory.clear()
