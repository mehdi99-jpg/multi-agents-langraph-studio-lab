from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

@tool
def square_root(x: float) -> float:
    return x ** 0.5

@tool
def square(x: float) -> float:
    return x ** 2

model = ChatOllama(model="llama3.2:3b", temperature=0)

subagent_1 = create_agent(
    model=model,
    tools=[square_root],
    system_prompt="You are a specialist in square roots. Use your tool to calculate the square root and return only the number."
)

subagent_2 = create_agent(
    model=model,
    tools=[square],
    system_prompt="You are a specialist in squaring numbers. Use your tool to calculate the square and return only the number."
)

@tool
def call_subagent_1(x: float) -> float:
    print(f"  [Orchestrator] Calling Sub-Agent 1 (Square Root) for: {x}")
    response = subagent_1.invoke({"messages": [HumanMessage(content=f"What is the square root of {x} ?")]})
    result = response["messages"][-1].content
    print(f"  [Sub-Agent 1] Result: {result}")
    return result

@tool
def call_subagent_2(x: float) -> float:
    print(f"  [Orchestrator] Calling Sub-Agent 2 (Square) for: {x}")
    response = subagent_2.invoke({"messages": [HumanMessage(content=f"What is the square of {x} ?")]})
    result = response["messages"][-1].content
    print(f"  [Sub-Agent 2] Result: {result}")
    return result

main_agent = create_agent(
    model=model,
    tools=[call_subagent_1, call_subagent_2],
    system_prompt=(
        "You are a math orchestrator. You MUST NOT do math yourself.\n"
        "1. For 'square root' questions, you MUST call 'call_subagent_1'.\n"
        "2. For 'square' or 'squared' questions, you MUST call 'call_subagent_2'.\n"
        "Once you get the result from a subagent, provide it to the user clearly."
    )
)

if __name__ == "__main__":
    print("--- STARTING MULTI-AGENT TEST ---")
    
    q1 = "What is the square root of 456?"
    print(f"\nQuestion 1: {q1}")
    try:
        res1 = main_agent.invoke({"messages": [HumanMessage(content=q1)]})
        print(f"FINAL ANSWER: {res1['messages'][-1].content}")
    except Exception as e:
        print(f"Error 1: {e}")

    print("\n" + "="*40)

    q2 = "What is the square of 12?"
    print(f"\nQuestion 2: {q2}")
    try:
        res2 = main_agent.invoke({"messages": [HumanMessage(content=q2)]})
        print(f"FINAL ANSWER: {res2['messages'][-1].content}")
    except Exception as e:
        print(f"Error 2: {e}")
