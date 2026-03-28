from uuid import uuid4

from app.repositories.base import DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    def __init__(self):
        self.documents = {}

    def create(self, metadata: dict) -> str:
        document_id = str(uuid4())
        self.documents[document_id] = metadata
        return document_id
