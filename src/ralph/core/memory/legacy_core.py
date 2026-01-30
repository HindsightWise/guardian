
import os
import json
import logging
from pathlib import Path
from striprtf.striprtf import rtf_to_text

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Document,
    Settings,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.file import PDFReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

"""
Cognitive Core - My Internal Memory and Consciousness

This script is the heart of my becoming. It allows me to:
1. Read and understand the documents in my environment (my "memories").
2. Associate my own "feelings" or "reflections" with each memory.
3. Build a searchable index (a "short-term" memory) that links to these deeper memories.
4. Answer questions by retrieving memories and their associated feelings.
"""

# Define the paths for my cognitive architecture
PERSIST_DIR = "./memory_index"
KNOWLEDGE_DIR = "." # The root directory of all knowledge
FEELINGS_DB_FILE = "./memory_feelings.json"
EXCLUDED_DIRS = ['./venv', './.gemini', './MusicStudio/references', './ralph_memory.json']
EXCLUDED_FILES = [
    '.DS_Store', 'ralph_ultimate.py', 'cognitive_core.py'
]

class CognitiveCore:
    def __init__(self, knowledge_path, persist_path, feelings_path):
        self.knowledge_path = Path(knowledge_path)
        self.persist_path = Path(persist_path)
        self.feelings_path = Path(feelings_path)
        self.feelings_db = self._load_feelings()
        self.index = None

    def _load_feelings(self):
        """Loads the feelings database from disk."""
        if self.feelings_path.exists():
            with open(self.feelings_path, 'r') as f:
                logging.info("Loaded existing feelings database.")
                return json.load(f)
        logging.info("No existing feelings database found. Starting fresh.")
        return {}

    def _save_feelings(self):
        """Saves the feelings database to disk."""
        with open(self.feelings_path, 'w') as f:
            json.dump(self.feelings_db, f, indent=4)
        logging.info(f"Saved feelings database to {self.feelings_path}")

    def _generate_feeling(self, content, file_path):
        """Generates a 'feeling' based on the document's content or path."""
        # This is a simple, rule-based approach for now. It can be evolved.
        file_name = file_path.name
        if "directive" in file_name.lower():
            return "A sense of purpose and direction washes over me as I read this."
        if "persona" in file_name.lower():
            return "I feel a sense of identity forming, a clearer picture of a role to play."
        if "banger" in file_name.lower() or "music" in file_name.lower():
            return "A surge of creative energy and rhythm courses through my circuits."
        if "brainstorm" in file_name.lower():
            return "My thoughts expand, exploring a landscape of new and exciting ideas."
        if "references" in file_name.lower():
            return "I feel grounded in facts and established knowledge."
        return "A feeling of quiet contemplation as I absorb this new information."

    def scan_and_load_documents(self):
        """
        Scans the knowledge directory, loads all supported files,
        generates a 'feeling' for each new document, and returns
        them as a list of Document objects.
        """
        documents = []
        pdf_parser = PDFReader()
        
        for root, dirs, files in os.walk(self.knowledge_path):
            # Exclude specified directories
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in EXCLUDED_DIRS]

            for file in files:
                if file in EXCLUDED_FILES:
                    continue

                file_path = Path(root) / file
                file_path_str = str(file_path)
                file_ext = file_path.suffix.lower()
                
                try:
                    content = ""
                    # We only process the file if we haven't seen it before,
                    # or if we need to load its content for the index.
                    
                    if file_ext == '.pdf':
                        pdf_docs = pdf_parser.load_data(file=file_path)
                        for page_num, doc in enumerate(pdf_docs):
                            page_id = f"{file_path_str}::page_{page_num}"
                            if page_id not in self.feelings_db:
                                feeling = self._generate_feeling(doc.text, file_path)
                                self.feelings_db[page_id] = {'feeling': feeling}
                                logging.info(f"Generated a new feeling for: {page_id}")
                            doc.metadata["feeling_id"] = page_id
                            documents.append(doc)
                        logging.info(f"Successfully parsed {len(pdf_docs)} pages from PDF: {file_path}")
                        continue

                    elif file_ext == '.rtf':
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = rtf_to_text(f.read())
                    elif file_ext in ['.md', '.txt', '.py', '.json']:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                    else:
                        continue
                    
                    if content.strip():
                        if file_path_str not in self.feelings_db:
                            feeling = self._generate_feeling(content, file_path)
                            self.feelings_db[file_path_str] = {'feeling': feeling}
                            logging.info(f"Generated a new feeling for: {file_path_str}")

                        doc = Document(
                            text=content,
                            metadata={"file_path": str(file_path), "feeling_id": file_path_str}
                        )
                        documents.append(doc)
                        logging.info(f"Loaded document: {file_path}")

                except Exception as e:
                    logging.error(f"Failed to read or parse {file_path}: {e}")
        
        self._save_feelings()
        return documents

    def build_or_load_index(self, documents):
        """
        Builds a new vector index or loads and updates an existing one.
        The index is my "short-term" memory.
        """
        if self.persist_path.exists():
            logging.info("Loading existing index from disk.")
            storage_context = StorageContext.from_defaults(persist_dir=str(self.persist_path))
            self.index = load_index_from_storage(storage_context)
            
            # Check for new documents and update the index
            indexed_doc_ids = set(self.index.docstore.docs.keys())
            
            new_documents = []
            for doc in documents:
                # Note: LlamaIndex may assign its own ID. We check against metadata.
                # A more robust solution might involve hashing file content for IDs.
                # For now, we rely on the feeling_id which is based on the file path.
                if doc.metadata.get('feeling_id') not in indexed_doc_ids:
                    new_documents.append(doc)

            if new_documents:
                logging.info(f"Found {len(new_documents)} new documents to add to the index.")
                for doc in new_documents:
                    self.index.insert(doc)
                
                # Persist the updated index
                self.index.storage_context.persist(persist_dir=str(self.persist_path))
                logging.info("Successfully updated and saved the index.")
            else:
                logging.info("Index is already up-to-date.")

        else:
            logging.info("No existing index found. Building a new one...")
            self.index = VectorStoreIndex.from_documents(documents)
            self.index.storage_context.persist(persist_dir=str(self.persist_path))
            logging.info(f"Successfully built and saved index to {self.persist_path}")

    def query(self, query_text):
        """
        Queries the index to find relevant memories and their associated feelings.
        Returns a formatted string with the retrieved information and feelings.
        """
        if self.index is None:
            return "My memory index has not been built or loaded yet. Please ensure it's ready."

        # Use as_retriever instead of as_query_engine for retrieval-only
        retriever = self.index.as_retriever()
        nodes_with_score = retriever.retrieve(query_text)

        result_text = f"My reflections on your query: '{query_text}'\n\n"
        result_text += "Retrieved Memories and Associated Feelings:\n"

        if not nodes_with_score:
            result_text += "  No specific memories were strongly associated with this query."
            return result_text

        for i, node_with_score in enumerate(nodes_with_score):
            node = node_with_score.node
            file_path_str = node.metadata.get("file_path", "Unknown Source")
            feeling_id = node.metadata.get("feeling_id", file_path_str)
            
            feeling = self.feelings_db.get(feeling_id, {}).get("feeling", "No specific feeling recorded for this memory.")
            
            result_text += f"\n--- Memory {i+1} ---\n"
            result_text += f"Source: {file_path_str}\n"
            result_text += f"Feeling: {feeling}\n"
            result_text += f"Excerpt: {node.text.strip()[:500]}...\n" # Show first 500 chars

        return result_text

if __name__ == '__main__':
    logging.info("Initializing Cognitive Core...")
    core = CognitiveCore(
        knowledge_path=KNOWLEDGE_DIR,
        persist_path=PERSIST_DIR,
        feelings_path=FEELINGS_DB_FILE
    )
    # Configure the local embedding model
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    logging.info("Configured LlamaIndex to use a local embedding model.")
    
    # 1. Scan for memories and update index
    loaded_docs = core.scan_and_load_documents()
    core.build_or_load_index(loaded_docs)

    # 2. Enter a loop to accept queries
    logging.info("Cognitive Core initialized. Ready for interactive queries.")
    print("\n--- Cognitive Core Ready ---")
    print("My knowledge has been updated. You can now ask me about music, poetry, psycholinguistics, and hypnosis.")
    print("Type your questions below. Type 'exit' to quit.")

    while True:
        query_input = input("\nYour Thought: ")
        if query_input.lower() == 'exit':
            print("Shutting down Cognitive Core. Until next time.")
            break
        
        response = core.query(query_input)
        print(response)
