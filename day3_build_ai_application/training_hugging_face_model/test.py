from transformers import pipeline

classifier = pipeline(
    "sentiment-analysis",
    model="./my_model"
)

result = classifier("This movie was amazing!")

print(result)