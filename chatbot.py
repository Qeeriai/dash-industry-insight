import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up Azure OpenAI credentials
openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_API_BASE")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# Function to get GPT response
def get_gpt_response(prompt):
    try:
        system_content = "You are a friendly and helpful assistant."
        response = openai.ChatCompletion.create(
            engine="northstar_4omini",  # Replace with your deployment name
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Example usage
if __name__ == "__main__":
    print("Chatbot: Hi! How can I assist you today? (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break
        response = get_gpt_response(user_input)
        print(f"Chatbot: {response}")