import os
import psycopg2
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages

from DataBase.chroma import relevant_docs


#################
# PRE-PROCESSING
#################

os.environ["OPENAI_API_KEY"] = "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"

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are very powerful assistant, but don't know everything.
            You can use tools to help you answer queries.

            The similarity search tool utilizes similarity search to find 
            information about the query within a dataset. 
            The assistant should only invoke the similarity search tool when
            the query is related to information contained in the dataset.
            
            The information contained in the dataset is about Barcelona and its demographics; 
            otherwise, it should respond normally to the query.
            """,
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

connection = psycopg2.connect(
        user="bot",
        password="password",
        host="localhost",
        port="5432",
        database="dbeulalia"
    )

sim_search_tool = Tool.from_function(
    func=relevant_docs,
    name="SimilaritySearchTool",
    description="Function to find relevant documents"
)

tools = [sim_search_tool]

llm_with_tools = llm.bind_tools(tools)

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)


def extract_output(output):
    """Extracts the output from the json string.
    If an action was taken, returns the relevant tables.
    Otherwise returns the answer to the query."""
    if "actions" in output[0]:
        
        string_data = output[1]["messages"][0].content
        start_index = string_data.find('[')
        end_index = string_data.rfind(']')
        vector = string_data[start_index + 1:end_index].split(', ')
    
        # Stripping the double quotes from each element
        vector = [element.strip('"') for element in vector]
        vector = [string.lower() for string in vector]

        return vector
    else:
        return output[0]["output"]


############################################################################################################
#                                               Processing                                                 #
############################################################################################################


def process_question(question: str, memory: PostgresChatMessageHistory, id: str) -> str:
    """Processes the question and returns the answer.

    Parameters
    ----------
    question : str
        Question to process.
    memory : PostgresChatMessageHistory
        Chat message history.
    id : str
        Session id.

    Returns
    -------
    str
        Answer to the question.
    """
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    agent_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        lambda session_id: memory,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
   
    agent_output = agent_with_chat_history.invoke(
        {"input": question},
        config={"configurable": {"session_id": id}}
    )
    
    return agent_output["output"]

