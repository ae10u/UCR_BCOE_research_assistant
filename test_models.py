import google.generativeai as genai
import os

# Wakes up the API using the key you exported in your terminal
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

print("Here are the exact models you can use right now:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)