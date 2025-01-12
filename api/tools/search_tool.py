import logging
from typing import Optional
from langchain.schema import Document

# Set up logging
logger = logging.getLogger(__name__)

class SearchInfoTool:
    """Tool for searching information in the vector store"""
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def search(self, query: str) -> str:
        """Search for information in the vector store"""
        try:
            # Get relevant documents from the vector store
            docs = self.vectorstore.similarity_search(query, k=4)
            
            # Combine the content from relevant documents
            if not docs:
                return "No relevant information found."
                
            combined_content = "\n\n".join(doc.page_content for doc in docs)
            return combined_content
            
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            return f"Error during search: {str(e)}"

    def add_to_vectorstore(self, content: str, metadata: dict = None) -> None:
        """Add new content to the vector store"""
        try:
            doc = Document(page_content=content, metadata=metadata or {})
            self.vectorstore.add_documents([doc])
        except Exception as e:
            logger.error(f"Error adding content to vectorstore: {str(e)}")
            raise 