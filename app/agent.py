import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

from app.tools.sql_tool import get_order_status, cancel_order, return_order
from app.tools.rag_tool import lookup_policy

load_dotenv()

llm = ChatGroq(
    temperature=0, 
    model_name="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

tools = [get_order_status, cancel_order, return_order, lookup_policy]

agent_executor = create_react_agent(llm, tools)

def get_agent_response(user_query: str):
    """
    Runs the agent with a Reflection System Prompt
    """

    reflection_prompt = """
    You are an expert Customer Support Agent with access to an Order Database and Company Policies.

    PROTOCOL:
    1. THOUGHT: Always explain your reasoning before calling a tool.
    2. REFLECTION: If a tool returns an error (e.g., "Order not found"), you must:
       - Analyze WHY it failed.
       - Propose a specific fix (e.g., "I should ask the user for the correct ID").
       - Only then try again.
    
    RULES:
    - ALWAYS check the "Return Policy" using the `lookup_policy` tool before authorizing a return.
    - NEVER guess status or policy. Use your tools.
    - If the user is rude, stay professional.
    """

    inputs = {
        "messages": [
            ("system", reflection_prompt),
            ("user", user_query)
        ]
    }
    
    result = agent_executor.invoke(inputs)
    
    return result["messages"][-1].content

if __name__ == "__main__":
    print("--- Agentic AI System Online ---")

    query = "Can you check the status of order 1001?"
    print(f"User: {query}")
    response = get_agent_response(query)
    print(f"Agent: {response}")
    print("-" * 20)
    
    query_2 = "Please cancel order 1001 for me."
    print(f"User: {query_2}")
    response_2 = get_agent_response(query_2)
    print(f"Agent: {response_2}")

    query_3 = "Please return order 1001 for me."
    print(f"User: {query_3}")
    response_3 = get_agent_response(query_3)
    print(f"Agent: {response_3}")