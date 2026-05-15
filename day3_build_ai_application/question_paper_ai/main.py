import ollama

# Improved prompt for specific structured output
prompt = """
Generate 5 Java Object-Oriented Programming (OOP) questions for a university exam.
For each question, provide:
1. The Question Text
2. Course Outcome (CO) Mapping (e.g., CO1, CO2)
3. Bloom's Taxonomy Level (e.g., Understand, Apply, Analyze)

Format each question as follows:
---
Q[Number]: [Question Text]
CO: [CO Mapping]
Level: [Bloom's Level]
---
"""

# Call ollama.chat with streaming enabled
stream = ollama.chat(
    model='gemma:2b',
    messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ],
    stream=True
)

print("Generating Questions...\n")

# Iterate through the stream and print content in real-time
for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)