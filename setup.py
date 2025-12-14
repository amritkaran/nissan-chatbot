"""
Setup script for Nissan Chatbot - OpenAI File Search Stack.
Handles end-to-end setup: scraping, vector store creation, and assistant configuration.
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def check_api_keys():
    """Check if required API keys are configured."""
    required_keys = {
        "OPENAI_API_KEY": "OpenAI",
        "FIRECRAWL_API_KEY": "Firecrawl",
    }

    optional_keys = {
        "DEEPGRAM_API_KEY": "Deepgram (voice transcription)",
        "ELEVENLABS_API_KEY": "ElevenLabs (text-to-speech)",
    }

    missing_required = []
    missing_optional = []

    print("\n=== Checking API Keys ===\n")

    for key, name in required_keys.items():
        value = os.getenv(key)
        if value:
            print(f"[OK] {name}: Configured")
        else:
            print(f"[X]  {name}: MISSING (Required)")
            missing_required.append(name)

    for key, name in optional_keys.items():
        value = os.getenv(key)
        if value:
            print(f"[OK] {name}: Configured")
        else:
            print(f"[!]  {name}: Not configured (Optional)")
            missing_optional.append(name)

    if missing_required:
        print(f"\n[ERROR] Missing required API keys: {', '.join(missing_required)}")
        print("Please add them to your .env file")
        return False

    if missing_optional:
        print(f"\n[WARNING] Voice features require: {', '.join(missing_optional)}")

    return True


def run_scraper():
    """Run the web scraper."""
    print("\n=== Running Web Scraper ===\n")

    result = subprocess.run(
        [sys.executable, "scraper/scraper.py"],
        capture_output=False,
    )

    if result.returncode != 0:
        print("[ERROR] Scraping failed")
        return False

    # Check if files were created
    processed_dir = Path("data/processed")
    if not processed_dir.exists() or not list(processed_dir.glob("*.md")):
        print("[ERROR] No processed files found")
        return False

    file_count = len(list(processed_dir.glob("*.md")))
    print(f"\n[OK] Scraped {file_count} pages successfully")
    return True


def setup_vector_store():
    """Create vector store and upload files."""
    print("\n=== Setting Up Vector Store ===\n")

    from backend.vector_store import VectorStoreManager

    manager = VectorStoreManager()

    # Create vector store
    vs_id = manager.get_or_create_vector_store("Nissan Knowledge Base")
    print(f"Vector Store ID: {vs_id}")

    # Upload files
    file_ids = manager.upload_files("data/processed", "*.md")

    if not file_ids:
        print("[ERROR] No files were uploaded")
        return None

    # Add to vector store
    success = manager.add_files_to_vector_store(file_ids)

    if not success:
        print("[ERROR] Failed to add files to vector store")
        return None

    # Get stats
    stats = manager.get_stats()
    print(f"\n[OK] Vector store ready")
    print(f"    Files: {stats.get('file_counts', {})}")

    return vs_id


def setup_assistant(vector_store_id: str):
    """Create the assistant with file search."""
    print("\n=== Setting Up Assistant ===\n")

    # Temporarily set the vector store ID for assistant creation
    os.environ["OPENAI_VECTOR_STORE_ID"] = vector_store_id

    from backend.assistant import NissanAssistant

    assistant = NissanAssistant()
    assistant.vector_store_id = vector_store_id

    # Create assistant
    assistant_id = assistant.create_assistant()
    print(f"Assistant ID: {assistant_id}")

    # Verify
    info = assistant.get_assistant_info()
    print(f"\n[OK] Assistant created")
    print(f"    Name: {info.get('name')}")
    print(f"    Model: {info.get('model')}")

    return assistant_id


def update_env_file(vector_store_id: str, assistant_id: str):
    """Update .env file with new IDs."""
    print("\n=== Updating .env File ===\n")

    env_path = Path(".env")

    if env_path.exists():
        content = env_path.read_text()
    else:
        # Copy from example
        example_path = Path(".env.example")
        if example_path.exists():
            content = example_path.read_text()
        else:
            content = ""

    # Update or add vector store ID
    if "OPENAI_VECTOR_STORE_ID=" in content:
        lines = content.split("\n")
        lines = [
            f"OPENAI_VECTOR_STORE_ID={vector_store_id}" if line.startswith("OPENAI_VECTOR_STORE_ID=") else line
            for line in lines
        ]
        content = "\n".join(lines)
    else:
        content += f"\nOPENAI_VECTOR_STORE_ID={vector_store_id}"

    # Update or add assistant ID
    if "OPENAI_ASSISTANT_ID=" in content:
        lines = content.split("\n")
        lines = [
            f"OPENAI_ASSISTANT_ID={assistant_id}" if line.startswith("OPENAI_ASSISTANT_ID=") else line
            for line in lines
        ]
        content = "\n".join(lines)
    else:
        content += f"\nOPENAI_ASSISTANT_ID={assistant_id}"

    env_path.write_text(content)
    print("[OK] .env file updated")
    print(f"    OPENAI_VECTOR_STORE_ID={vector_store_id}")
    print(f"    OPENAI_ASSISTANT_ID={assistant_id}")


def test_assistant():
    """Run a quick test of the assistant."""
    print("\n=== Testing Assistant ===\n")

    load_dotenv()  # Reload env vars

    from backend.assistant import NissanAssistant

    assistant = NissanAssistant()

    if not assistant.assistant_id:
        print("[ERROR] Assistant ID not found in environment")
        return False

    # Test question
    test_question = "What vehicles does Nissan make?"
    print(f"Test Question: {test_question}")
    print("-" * 40)

    thread_id = assistant.create_thread()
    response = assistant.send_message(thread_id, test_question)

    print(f"Response: {response[:500]}...")
    print("-" * 40)
    print("[OK] Assistant is working!")
    return True


def main():
    """Run full setup process."""
    print("=" * 60)
    print("     NISSAN CHATBOT SETUP - OpenAI File Search Stack")
    print("=" * 60)

    import argparse

    parser = argparse.ArgumentParser(description="Setup Nissan chatbot")
    parser.add_argument("--skip-scrape", action="store_true", help="Skip web scraping")
    parser.add_argument("--skip-test", action="store_true", help="Skip assistant test")
    args = parser.parse_args()

    # Step 1: Check API keys
    if not check_api_keys():
        print("\n[FAILED] Setup cannot continue without required API keys")
        return 1

    # Step 2: Run scraper
    if not args.skip_scrape:
        if not run_scraper():
            print("\n[FAILED] Scraping step failed")
            return 1
    else:
        print("\n[SKIP] Scraping step skipped")

    # Step 3: Setup vector store
    vector_store_id = setup_vector_store()
    if not vector_store_id:
        print("\n[FAILED] Vector store setup failed")
        return 1

    # Step 4: Setup assistant
    assistant_id = setup_assistant(vector_store_id)
    if not assistant_id:
        print("\n[FAILED] Assistant setup failed")
        return 1

    # Step 5: Update .env
    update_env_file(vector_store_id, assistant_id)

    # Step 6: Test assistant
    if not args.skip_test:
        if not test_assistant():
            print("\n[WARNING] Assistant test failed, but setup completed")
    else:
        print("\n[SKIP] Assistant test skipped")

    print("\n" + "=" * 60)
    print("                    SETUP COMPLETE!")
    print("=" * 60)
    print("""
Next Steps:
-----------
1. Start the backend API:
   python backend/api.py

2. Start the frontend (in another terminal):
   cd frontend && npm install && npm run dev

3. Open http://localhost:3000 in your browser

4. Run evaluation (optional):
   python evaluation/evaluate.py
""")

    return 0


if __name__ == "__main__":
    sys.exit(main())
