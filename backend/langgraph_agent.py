from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.errors import GraphRecursionError
import langgraph_tools
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bind tools
tools = [
    langgraph_tools.find_hcp,
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
    temperature=0.1,
    max_retries=2,
)

# Create ReAct agent graph
agent_graph = create_react_agent(llm, tools)

# System message to guide the agent workflow
import datetime
CURRENT_DATETIME = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
SYSTEM_MESSAGE = SystemMessage(content=f"""You are a CRM assistant for logging HCP (Healthcare Professional) interactions.
The current date/time is: {CURRENT_DATETIME}

When a user asks to "log an interaction" or "record a meeting" with an HCP:
1. FIRST, use find_hcp tool to find the HCP by name and get their hcp_id
2. Then IMMEDIATELY call log_interaction with: hcp_id from step 1, date_time="{CURRENT_DATETIME}", interaction_type="in_person", topics_discussed="<topics from user message>"
3. Do NOT stop after find_hcp - you MUST also call log_interaction to complete the user's request

Example workflow for "Log an interaction with Dr. Smith about cardiology":
- Call find_hcp(name="Dr. Smith") -> get hcp_id=2
- Call log_interaction(hcp_id=2, date_time="{CURRENT_DATETIME}", interaction_type="in_person", topics_discussed="cardiology")

Available tools: find_hcp, log_interaction, edit_interaction, search_hcp_history, schedule_followup, log_sample_distribution
""")

def invoke_agent(user_message: str) -> str:
    """Invoke the LangGraph agent with a user message and return the response."""
    try:
        logger.info(f"Invoking agent with message: {user_message}")
        result = agent_graph.invoke(
            {"messages": [SYSTEM_MESSAGE, HumanMessage(content=user_message)]},
            {"recursion_limit": 10}
        )
        logger.info("Agent invocation completed successfully")
        if result and "messages" in result:
            # Look for tool messages with JSON output
            for msg in reversed(result["messages"]):
                if hasattr(msg, 'content') and msg.content.startswith('{'):
                    try:
                        import json
                        json.loads(msg.content)
                        logger.info("Found JSON tool response")
                        return msg.content
                    except:
                        pass
            # Fallback: return last message content
            final_message = result["messages"][-1]
            return final_message.content if hasattr(final_message, 'content') else str(final_message)
        return "Agent returned no response"
    except GraphRecursionError:
        logger.error("Agent hit recursion limit")
        return '{"action": "error", "status": "error", "message": "Agent exceeded recursion limit - check tool calls"}'
    except Exception as e:
        logger.error(f"Error invoking agent: {str(e)}", exc_info=True)
        return f'{{"action": "error", "status": "error", "message": "{str(e)}"}}'
