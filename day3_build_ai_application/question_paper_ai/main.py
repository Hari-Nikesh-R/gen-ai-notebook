import ollama

response = ollama.chat(
    model='gemma:2b',
    messages=[
        {
            'role': 'user',
            'content': '''
            Generate 5 Java OOP questions with CO mapping
            '''
        }
    ]
)

print(response['message']['content'])