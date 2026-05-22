from langchain_community.llms import Ollama
from langchain_classic.agents import initialize_agent
from langchain_classic.agents import Tool
from langchain_classic.agents import AgentType
import math


# -----------------------------
# LOCAL LLM
# -----------------------------
llm = Ollama(model="gemma4")


# -----------------------------
# TOOL 1 : Calculator
# -----------------------------
def calculator_tool(query):
    try:
        result = eval(query)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


# -----------------------------
# TOOL 2 : Square Root
# -----------------------------
def sqrt_tool(query):
    try:
        number = float(query)
        return str(math.sqrt(number))
    except Exception as e:
        return f"Error: {str(e)}"


# -----------------------------
# TOOLS LIST
# -----------------------------
tools = [
    Tool(
        name="Calculator",
        func=calculator_tool,
        description="Useful for mathematical calculations"
    ),

    Tool(
        name="SquareRoot",
        func=sqrt_tool,
        description="Useful for square root calculations"
    )
]


# -----------------------------
# AGENT
# -----------------------------
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)


# -----------------------------
# USER QUERY
# -----------------------------
query = input("Ask Something: ")

response = agent.run(query)

print("\nFINAL ANSWER:")
print(response)
