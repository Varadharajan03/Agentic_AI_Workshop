import os
from typing import TypedDict, Annotated, List
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
import re

os.environ["GROQ_API_KEY"] = "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"

class State(TypedDict):
    messages: Annotated[List, add_messages]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",  
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

@tool
def plus(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

@tool
def subtract(a: float, b: float) -> float:
    """Subtract the second number from the first number."""
    return a - b

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

@tool
def divide(a: float, b: float) -> float:
    """Divide the first number by the second number."""
    if b == 0:
        raise ValueError("Cannot divide by zero!")
    return a / b

tools = [plus, subtract, multiply, divide]

llm_with_tools = llm.bind_tools(tools)

tool_node = ToolNode(tools)

def chatbot(state: State):
    """Main chatbot node that processes messages and decides whether to use tools."""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def should_continue(state: State):
    """Determine whether to continue to tools or end the conversation."""
    messages = state['messages']
    last_message = messages[-1]
    
    if last_message.tool_calls:
        return "tools"
    return END

def create_agent_graph():
    """Create and compile the LangGraph agent."""
    workflow = StateGraph(State)
    
    workflow.add_node("agent", chatbot)
    workflow.add_node("tools", tool_node)
    
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    
    workflow.add_edge("tools", "agent")
    
    app = workflow.compile()
    return app

def is_math_query(query: str) -> bool:
    """Check if the query contains mathematical operations."""
    math_keywords = [
        'add', 'plus', 'sum', 'addition',
        'subtract', 'minus', 'difference', 'subtraction',
        'multiply', 'times', 'product', 'multiplication',
        'divide', 'division', 'quotient',
        'calculate', 'compute', 'solve'
    ]
    
    math_symbols = ['+', '-', '*', '/', '×', '÷']
    
    query_lower = query.lower()
    
    for keyword in math_keywords:
        if keyword in query_lower:
            return True
    
    for symbol in math_symbols:
        if symbol in query:
            return True
    
    number_pattern = r'\b\d+(?:\.\d+)?\b'
    numbers = re.findall(number_pattern, query)
    
    if len(numbers) >= 2 and any(keyword in query_lower for keyword in math_keywords):
        return True
    
    return False

def run_agent():
    """Main function to interact with the agent."""
    print("🤖 LangGraph Mathematical Agent")
    print("=" * 50)
    print("I can answer general questions and perform mathematical operations!")
    print("Mathematical operations: addition, subtraction, multiplication, division")
    print("Type 'quit' or 'exit' to end the conversation.\n")
    
    agent = create_agent_graph()
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            initial_state = {
                "messages": [HumanMessage(content=user_input)]
            }
            
            if is_math_query(user_input):
                enhanced_prompt = f"""The user is asking a mathematical question: "{user_input}"

Please identify the mathematical operation needed and use the appropriate tool:
- For addition: use the plus(a, b) tool
- For subtraction: use the subtract(a, b) tool  
- For multiplication: use the multiply(a, b) tool
- For division: use the divide(a, b) tool

Extract the numbers from the question and call the appropriate tool."""
                
                initial_state = {
                    "messages": [HumanMessage(content=enhanced_prompt)]
                }
            
            result = agent.invoke(initial_state)
            
            final_message = result["messages"][-1]
            
            if hasattr(final_message, 'content'):
                response = final_message.content
            else:
                response = str(final_message)
            
            print(f"🤖 Agent: {response}\n")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")

def test_agent():
    """Test the agent with various queries."""
    print("🧪 Testing the LangGraph Mathematical Agent")
    print("=" * 50)
    
    agent = create_agent_graph()
    
    test_queries = [
        "What is 5 plus 3?",
        "Calculate 10 minus 4",
        "What's 7 times 8?",
        "Divide 20 by 4",
        "What is the capital of France?",
        "How does photosynthesis work?",
        "What is 15 divided by 0?",  
        "Add 2.5 and 3.7",
        "What's the weather like today?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: '{query}'")
        print("-" * 40)
        
        try:
            if is_math_query(query):
                enhanced_prompt = f"""The user is asking a mathematical question: "{query}"

Please identify the mathematical operation needed and use the appropriate tool:
- For addition: use the plus(a, b) tool
- For subtraction: use the subtract(a, b) tool  
- For multiplication: use the multiply(a, b) tool
- For division: use the divide(a, b) tool

Extract the numbers from the question and call the appropriate tool."""
                
                initial_state = {
                    "messages": [HumanMessage(content=enhanced_prompt)]
                }
            else:
                initial_state = {
                    "messages": [HumanMessage(content=query)]
                }
            
            result = agent.invoke(initial_state)
            
            final_message = result["messages"][-1]
            response = final_message.content if hasattr(final_message, 'content') else str(final_message)
            
            print(f"Response: {response}")
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":

    run_agent()
