from elasticsearch import Elasticsearch
from app.config import settings


class ESClient:
    def __init__(self):
        self.client = Elasticsearch(settings.ELASTICSEARCH_URL)
    
    def index_document(self, index: str, doc: dict, doc_id: str = None):
        if doc_id:
            self.client.index(index=index, id=doc_id, body=doc)
        else:
            self.client.index(index=index, body=doc)
    
    def search(self, index: str, query: dict):
        return self.client.search(index=index, body=query)
    
    def delete_document(self, index: str, doc_id: str):
        self.client.delete(index=index, id=doc_id)
    
    def create_index(self, index: str, mappings: dict = None):
        if not self.client.indices.exists(index=index):
            if mappings:
                self.client.indices.create(index=index, body=mappings)
            else:
                self.client.indices.create(index=index)


es_client = ESClient()
