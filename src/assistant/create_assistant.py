from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

with open("src/agent/prompts/system_prompt.txt", "r")as f:
    system_prompt = f.read()

with open("src/agent/prompts/personality.txt", "r") as f:
    personality = f.read()

instructions = system_prompt + "\n\n" + personality

client = OpenAI()

assistant = client.beta.assistants.create(
    name = "Finance Assistant",
    instructions= instructions,
    model='gpt-4.1'
)

print("Assistant created with ID", assistant.id)
with open("assistant_id.txt", "w") as f:
    f.write(assistant.id)