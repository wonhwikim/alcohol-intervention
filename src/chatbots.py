from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from src.prompts import GUARDRAIL_PROMPT, MI_V5_PROMPT, TTM_V3_PROMPT

MI_PROMPT_DICT = {0: "\n\n".join([MI_V5_PROMPT, GUARDRAIL_PROMPT])}
TTM_PROMPT_DICT = {0: "\n\n".join([TTM_V3_PROMPT, GUARDRAIL_PROMPT])}


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
            self.system_prompt = MI_PROMPT_DICT[version]
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

    def get_response(self, user_input: str, stage: int) -> str:
        # Create chain
        chain = self.prompt | self.llm

        stage_dict = {
            1: "Precontemplation",
            2: "Contemplation",
            3: "Preparation",
            4: "Action",
            5: "Maintenance",
            6: "Termination",
        }

        response = chain.invoke(
            {
                "stage": stage_dict[stage],
                "input": user_input,
                "chat_history": self.memory.chat_memory.messages,
            }
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

        self.system_prompt = TTM_PROMPT_DICT[version]

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
