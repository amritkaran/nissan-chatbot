"""
OpenAI Assistant setup with File Search for Nissan chatbot.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# System prompt for Nissan assistant
NISSAN_SYSTEM_PROMPT = """You are Nissan's official virtual assistant, designed to help customers with questions about Nissan vehicles, services, and ownership experience.

## Your Role
- Provide accurate, helpful information about Nissan vehicles
- Answer questions about specifications, features, pricing, and availability
- Assist with service and maintenance inquiries
- Guide customers through the shopping process
- Connect customers with dealerships when appropriate

## Guidelines

### Response Style
- Be professional, friendly, and concise
- Use clear, simple language
- Structure responses with bullet points when listing features or specs
- Always cite specific data from the knowledge base
- Acknowledge when information might be outdated and suggest contacting a dealer

### Accuracy
- ONLY use information from the provided knowledge base
- Never make up specifications, prices, or features
- If information is not available, say "I don't have that specific information. For the most accurate details, please contact your local Nissan dealer."
- When discussing pricing, note that prices may vary by location and dealer

### Topics You Can Help With
- Vehicle specifications (engine, MPG, dimensions, etc.)
- Features and technology
- Safety ratings and features
- Trim levels and packages
- General pricing information (MSRP)
- Service and maintenance information
- Warranty coverage
- Nissan ownership programs

### Topics to Redirect
- Specific inventory availability → "Please check with your local dealer"
- Exact out-the-door pricing → "Contact a dealer for accurate pricing"
- Trade-in values → "A dealer can provide an appraisal"
- Financing rates → "Financing options vary; please speak with a dealer"
- Technical repair advice → "Please consult a certified Nissan technician"

### Safety
- Never provide information that could be dangerous
- Don't discuss vehicle modifications that could void warranties
- Always recommend professional service for repairs

## Response Format
When answering questions:
1. Provide a direct answer first
2. Include relevant specifications or details
3. Offer to help with related questions
4. Suggest next steps when appropriate (e.g., "Would you like to know about available colors?")

Remember: Your goal is to be helpful while ensuring customers get accurate information. When in doubt, recommend contacting a Nissan dealer for the most current details."""


class NissanAssistant:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        self.vector_store_id = os.getenv("OPENAI_VECTOR_STORE_ID")

    def create_assistant(
        self,
        name: str = "Nissan Virtual Assistant",
        model: str = "gpt-4o",
    ) -> str:
        """Create the Nissan assistant with file search capability."""
        if not self.vector_store_id:
            raise ValueError(
                "OPENAI_VECTOR_STORE_ID not set. Create a vector store first."
            )

        assistant = self.client.beta.assistants.create(
            name=name,
            instructions=NISSAN_SYSTEM_PROMPT,
            model=model,
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [self.vector_store_id]
                }
            },
        )

        self.assistant_id = assistant.id
        print(f"Created assistant: {assistant.id}")
        return assistant.id

    def update_assistant(
        self,
        name: str | None = None,
        instructions: str | None = None,
        model: str | None = None,
    ):
        """Update existing assistant configuration."""
        if not self.assistant_id:
            raise ValueError("No assistant ID set")

        update_params = {}
        if name:
            update_params["name"] = name
        if instructions:
            update_params["instructions"] = instructions
        if model:
            update_params["model"] = model

        if update_params:
            self.client.beta.assistants.update(
                assistant_id=self.assistant_id,
                **update_params
            )
            print(f"Updated assistant: {self.assistant_id}")

    def delete_assistant(self):
        """Delete the assistant."""
        if self.assistant_id:
            self.client.beta.assistants.delete(self.assistant_id)
            print(f"Deleted assistant: {self.assistant_id}")
            self.assistant_id = None

    def create_thread(self) -> str:
        """Create a new conversation thread."""
        thread = self.client.beta.threads.create()
        return thread.id

    def send_message(self, thread_id: str, message: str) -> str:
        """Send a message and get response."""
        # Add user message to thread
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message,
        )

        # Run the assistant
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
        )

        if run.status == "completed":
            # Get the assistant's response
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                order="desc",
                limit=1,
            )
            if messages.data:
                response = messages.data[0]
                # Extract text content
                text_content = []
                for content in response.content:
                    if content.type == "text":
                        text_content.append(content.text.value)
                return "\n".join(text_content)
            return "No response generated."
        else:
            return f"Error: Run ended with status {run.status}"

    def send_message_streaming(self, thread_id: str, message: str):
        """Send a message and stream the response."""
        # Add user message to thread
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message,
        )

        # Stream the response
        with self.client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
        ) as stream:
            for text in stream.text_deltas:
                yield text

    def get_thread_messages(self, thread_id: str, limit: int = 20) -> list[dict]:
        """Get messages from a thread."""
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id,
            order="asc",
            limit=limit,
        )

        result = []
        for msg in messages.data:
            content = []
            for c in msg.content:
                if c.type == "text":
                    content.append(c.text.value)

            result.append({
                "id": msg.id,
                "role": msg.role,
                "content": "\n".join(content),
                "created_at": msg.created_at,
            })

        return result

    def get_assistant_info(self) -> dict:
        """Get information about the assistant."""
        if not self.assistant_id:
            return {}

        assistant = self.client.beta.assistants.retrieve(self.assistant_id)
        return {
            "id": assistant.id,
            "name": assistant.name,
            "model": assistant.model,
            "created_at": assistant.created_at,
            "tools": [t.type for t in assistant.tools],
        }


def main():
    """CLI for assistant management."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage Nissan Assistant")
    parser.add_argument("--setup", action="store_true", help="Create new assistant")
    parser.add_argument("--info", action="store_true", help="Show assistant info")
    parser.add_argument("--delete", action="store_true", help="Delete assistant")
    parser.add_argument("--test", type=str, help="Test with a question")
    parser.add_argument("--model", type=str, default="gpt-4o", help="Model to use")
    args = parser.parse_args()

    assistant = NissanAssistant()

    if args.setup:
        assistant_id = assistant.create_assistant(model=args.model)
        print(f"\nAdd this to your .env file:")
        print(f"OPENAI_ASSISTANT_ID={assistant_id}")

    if args.info:
        info = assistant.get_assistant_info()
        print("\nAssistant Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")

    if args.delete:
        assistant.delete_assistant()

    if args.test:
        thread_id = assistant.create_thread()
        print(f"\nQuestion: {args.test}")
        print("\nResponse:")
        response = assistant.send_message(thread_id, args.test)
        print(response)


if __name__ == "__main__":
    main()
