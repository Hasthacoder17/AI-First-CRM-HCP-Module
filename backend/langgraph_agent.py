from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
import langgraph_tools
import config

# Bind tools
tools = [
    langgraph_tools.log_interaction,
    langgraph_tools.edit_interaction,
    langgraph_tools.search_hcp_history,
    langgraph_tools.schedule_followup,
    langgraph_tools.log_sample_distribution,
]

# Initialize LLM
llm = ChatGroq(
    groq_api_key=config.GROQ_API_KEY,
    model_name=config.GROQ_MODEL,
    temperature=0.1
)

# Create ReAct agent graph
agent_graph = create_react_agent(llm, tools)

def invoke_agent(user_message: str) -> str:
    """Invoke the LangGraph agent with a user message and return the response."""
    try:
        result = agent_graph.invoke({"messages": [HumanMessage(content=user_message)]})
        if result and "messages" in result:
            final_message = result["messages"][-1]
            return final_message.content if hasattr(final_message, 'content') else str(final_message)
        return "Agent returned no response"
    except Exception as e:
        return f"Error invoking agent: {str(e)}"
