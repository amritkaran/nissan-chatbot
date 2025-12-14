"""
OpenAI Vector Store management for Nissan knowledge base.
Handles file uploads, vector store creation, and management.
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

load_dotenv()


class VectorStoreManager:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.vector_store_id = os.getenv("OPENAI_VECTOR_STORE_ID")

    def create_vector_store(self, name: str = "Nissan Knowledge Base") -> str:
        """Create a new vector store."""
        vector_store = self.client.vector_stores.create(
            name=name,
            expires_after={
                "anchor": "last_active_at",
                "days": 30  # Auto-expire after 30 days of inactivity
            }
        )
        print(f"Created vector store: {vector_store.id}")
        self.vector_store_id = vector_store.id
        return vector_store.id

    def get_or_create_vector_store(self, name: str = "Nissan Knowledge Base") -> str:
        """Get existing vector store or create new one."""
        if self.vector_store_id:
            try:
                # Verify it exists
                self.client.vector_stores.retrieve(self.vector_store_id)
                print(f"Using existing vector store: {self.vector_store_id}")
                return self.vector_store_id
            except Exception:
                print("Existing vector store not found, creating new one...")

        return self.create_vector_store(name)

    def upload_files(self, directory: str | Path, file_pattern: str = "*.md") -> list[str]:
        """Upload files to OpenAI and return file IDs."""
        directory = Path(directory)
        files = list(directory.glob(file_pattern))

        if not files:
            print(f"No files matching {file_pattern} found in {directory}")
            return []

        print(f"Uploading {len(files)} files...")
        file_ids = []

        for filepath in tqdm(files, desc="Uploading"):
            try:
                with open(filepath, "rb") as f:
                    file_obj = self.client.files.create(
                        file=f,
                        purpose="assistants"
                    )
                    file_ids.append(file_obj.id)
            except Exception as e:
                print(f"Error uploading {filepath}: {e}")

        return file_ids

    def add_files_to_vector_store(self, file_ids: list[str]) -> bool:
        """Add uploaded files to vector store."""
        if not self.vector_store_id:
            raise ValueError("No vector store ID set. Create one first.")

        if not file_ids:
            print("No files to add")
            return False

        print(f"Adding {len(file_ids)} files to vector store...")

        # Use batch upload for efficiency
        batch = self.client.vector_stores.file_batches.create(
            vector_store_id=self.vector_store_id,
            file_ids=file_ids
        )

        # Poll until complete
        while batch.status in ["validating", "in_progress"]:
            print(f"Status: {batch.status} - Files: {batch.file_counts}")
            time.sleep(2)
            batch = self.client.vector_stores.file_batches.retrieve(
                vector_store_id=self.vector_store_id,
                batch_id=batch.id
            )

        if batch.status == "completed":
            print(f"Successfully added files to vector store")
            print(f"File counts: {batch.file_counts}")
            return True
        else:
            print(f"Batch failed with status: {batch.status}")
            return False

    def list_files(self) -> list[dict]:
        """List all files in the vector store."""
        if not self.vector_store_id:
            return []

        files = self.client.vector_stores.files.list(
            vector_store_id=self.vector_store_id
        )
        return [{"id": f.id, "status": f.status} for f in files.data]

    def delete_all_files(self):
        """Delete all files from vector store."""
        if not self.vector_store_id:
            return

        files = self.list_files()
        for file in tqdm(files, desc="Deleting files"):
            try:
                self.client.vector_stores.files.delete(
                    vector_store_id=self.vector_store_id,
                    file_id=file["id"]
                )
            except Exception as e:
                print(f"Error deleting {file['id']}: {e}")

    def delete_vector_store(self):
        """Delete the vector store."""
        if self.vector_store_id:
            self.client.vector_stores.delete(self.vector_store_id)
            print(f"Deleted vector store: {self.vector_store_id}")
            self.vector_store_id = None

    def get_stats(self) -> dict:
        """Get vector store statistics."""
        if not self.vector_store_id:
            return {}

        vs = self.client.vector_stores.retrieve(self.vector_store_id)
        return {
            "id": vs.id,
            "name": vs.name,
            "status": vs.status,
            "file_counts": vs.file_counts,
            "usage_bytes": vs.usage_bytes,
            "created_at": vs.created_at,
        }


def main():
    """CLI for vector store management."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage OpenAI Vector Store")
    parser.add_argument("--create", action="store_true", help="Create new vector store")
    parser.add_argument("--upload", type=str, help="Upload files from directory")
    parser.add_argument("--list", action="store_true", help="List files in vector store")
    parser.add_argument("--stats", action="store_true", help="Show vector store stats")
    parser.add_argument("--delete-files", action="store_true", help="Delete all files")
    parser.add_argument("--delete-store", action="store_true", help="Delete vector store")
    args = parser.parse_args()

    manager = VectorStoreManager()

    if args.create:
        vs_id = manager.create_vector_store()
        print(f"\nAdd this to your .env file:")
        print(f"OPENAI_VECTOR_STORE_ID={vs_id}")

    if args.upload:
        vs_id = manager.get_or_create_vector_store()
        file_ids = manager.upload_files(args.upload)
        if file_ids:
            manager.add_files_to_vector_store(file_ids)

    if args.list:
        files = manager.list_files()
        print(f"\nFiles in vector store ({len(files)}):")
        for f in files:
            print(f"  - {f['id']}: {f['status']}")

    if args.stats:
        stats = manager.get_stats()
        print("\nVector Store Stats:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    if args.delete_files:
        manager.delete_all_files()

    if args.delete_store:
        manager.delete_vector_store()


if __name__ == "__main__":
    main()
