from uuid import uuid4

from app.repositories.base import DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    def __init__(self):
        self.documents = {}

    def create(self, name: str, metadata: dict) -> str:
        document_id = str(uuid4())
        self.documents[document_id] = {"name": name, "metadata": metadata}
        return document_id
