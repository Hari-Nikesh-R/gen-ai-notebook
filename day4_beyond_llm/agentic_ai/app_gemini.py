import google.generativeai as genai
import math


# --------------------------------
# CONFIGURE API
# --------------------------------
genai.configure(api_key="YOUR_API_KEY")


# --------------------------------
# LOAD MODEL
# --------------------------------
model = genai.GenerativeModel("gemini-1.5-flash")


# --------------------------------
# TOOLS
# --------------------------------
def calculator(query):
    try:
        return str(eval(query))
    except Exception as e:
        return str(e)


def square_root(query):
    try:
        return str(math.sqrt(float(query)))
    except Exception as e:
        return str(e)


# --------------------------------
# SIMPLE AGENT LOOP
# --------------------------------
while True:

    user = input("\nAsk: ")

    prompt = f"""
    You are an AI agent.

    Available tools:
    1. calculator
    2. square_root

    User query:
    {user}

    Decide:
    - Which tool to use
    - What input to pass
    """

    response = model.generate_content(prompt)

    answer = response.text

    print("\nAgent Thinking:")
    print(answer)
