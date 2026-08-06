
import warnings
# Make src/ importable when running from project root
warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys
import os
import re
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.assistant.models.bill import Bill
from src.assistant.utils.identity import bill_identity_provider
from src.assistant.store.bill_store import BillStore
from src.assistant.utils.bill_parser import parse_bill_fields
from src.assistant.tools.add_bill import add_bill_tool
Bill.identity_provider = bill_identity_provider


from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()
bill_store = BillStore()
from assistant.memory.memory import load_memory, save_memory
memory = load_memory()

# Tool registry: add tools here as you build them
TOOLS = {
    "add_bill": add_bill_tool,
}

# Load assistant ID
with open("assistant_id.txt", "r") as f:
    assistant_id = f.read().strip()

# Create a thread
thread = client.beta.threads.create()

# Greeting using assistant_name if set
assistant_label = memory.get("assistant_name", "Assistant")
if memory.get("user_name"):
    print(f"{assistant_label}: Welcome back, {memory['user_name']}!")
    print()




def generate_ai_goodbye(client, thread_id, assistant_id):
    # Step 1: Add the goodbye request as a user message
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=(
            "Create a short warm goodbye message addressed to Steve. "
            "Keep it friendly, positive, and in the assistant's personality. "
            "Use a tone that feels encouraging and lightly playful."
            "Do not ask questions. Do not continue the conversation."
        )
    )

    # Step 2: Run the assistant to generate the reply
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Step 3: Poll until the run is complete
    while True:
        status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if status.status == "completed":
            break

    # Step 4: Fetch the assistant's latest message
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    assistant_message = messages.data[0]  # newest message

    return assistant_message.content[0].text.value


# Conversational loop
while True:
    user_input = input("You: ")

    if not user_input.strip():
        continue
     
    if user_input.lower() in ["exit", "quit", "done", "bye"]:
        goodbye = generate_ai_goodbye(client, thread.id, assistant_id)
        print(f"{assistant_label}: {goodbye}")
        break
    # Natural-language bill detection
    
    if re.search(r"\badd\b.*\bbill\b", user_input.lower()):
        fields = parse_bill_fields(user_input)
        # Map parser output to valid enums
        category = fields["category"] or "other"
        frequency = fields["frequency"] or "onetime"
        
        result = TOOLS["add_bill"](
            name=fields["name"],
            amount=fields["amount"],
            due_date=str(fields["due_date"]),
            category= category,
            pay_type= frequency
        )

        print(f"\n{assistant_label}: {result['message']} (ID: {result['id']}, Alias: {result['alias']})\n")
        continue


    # # Tool command detection ** Marked for deletion **
    # if user_input.startswith("add bill"):
    #     parts = user_input.split()
    #     if len(parts) >= 7:
    #         _, _, name, amount, due_date, category, pay_type = parts[:7]
    #         result = TOOLS["add_bill"](
    #             name=name,
    #             amount=float(amount),
    #             due_date=due_date,
    #             category=category,
    #             pay_type=pay_type
    #         )
    #     print(f"\n{assistant_label}: {result['message']} (ID: {result['id']}, Alias: {result['alias']})\n")
    #     continue


    # Detect user name
    if "my name is" in user_input.lower():
        name = user_input.split("my name is", 1)[1].strip()
        memory["user_name"] = name
        save_memory(memory)
       
        assistant_label = memory.get("assistant_name", "Assistant")
        print(f"\n{assistant_label}: Nice to meet you, {name}!\n")
        continue

    # Detect assistant name
    if "your name is" in user_input.lower():
        name = user_input.split("your name is", 1)[1].strip()
        memory["assistant_name"] = name
        save_memory(memory)
        print(f"\n{name}: Nice to meet you!\n")
        continue


    # Send user message
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    # Start a run
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    # Poll until run completes
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        if run.status == "completed":
            break

        if run.status == "requires_action":
            break

    # Get messages for this thread
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    # Use assistant_name if set, otherwise "Assistant"
    assistant_label = memory.get("assistant_name", "Assistant")

    # ✅ messages.data is already newest-first, so we DO NOT reverse it.
    for msg in messages.data:
        if msg.role == "assistant":
            print("\n\n")
            print(f"{assistant_label}:", msg.content[0].text.value)
            print("\n\n")
            break
