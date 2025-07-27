from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")

output = generator("Hello, how are you today?", max_length=50)

print(output[0]['generated_text'])
