import os
import torch
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchText, SearchParams
from transformers import AutoTokenizer, AutoModel
from util import *


#######################################################
#####################  SEARCH  ########################
#######################################################


class NeuralSearcher:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        
        # Initialize encoder model from huggingface (requires internet every time)
        # self.tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-base-en-v1.5")
        # self.model = AutoModel.from_pretrained("BAAI/bge-base-en-v1.5")

        # Initialize encoder model locally and offline
        local_directory =  install_path() + "/models/BAII/"
        self.tokenizer = AutoTokenizer.from_pretrained(local_directory)
        self.model = AutoModel.from_pretrained(local_directory)

        self.model.eval()  # Set the model to evaluation mode
        # initialize Qdrant client
        self.qdrant_client = QdrantClient(f"{config('search','qdrant_url')}")


    def encode(self, text: str):
        # Tokenize and encode
        inputs = self.tokenizer(text, return_tensors="pt", max_length=512, truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        # Use the [CLS] token embedding as the sentence embedding
        embeddings = outputs.last_hidden_state[:, 0, :]
        # Normalize the embeddings
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        return embeddings.squeeze().tolist()

    # from prompt quill
    def get_context_filter(self, filter_text,blocklist_text):

        must = []
        must_not = []
        if filter_text:
            if len(filter_text) > 0:
                for word in filter_text.split(','):
                    must.append(
                        FieldCondition(
                            key="search",
                            match=MatchText(text=f"{word.strip()}"),
                        )
                    )
        if blocklist_text:
            if len(blocklist_text) > 0:
                for word in blocklist_text.split(','):
                    must_not.append(
                        FieldCondition(
                            key="search",
                            match=MatchText(text=f"{word.strip()}"),
                        )
                    )

        if len(must) < 1:
            must = None
        if len(must_not) < 1:
            must_not = None
        filter = Filter(must=must,
                        must_not=must_not)
        return filter

    def search(self, text: str, filter_text: str = None):
        #Convert text query into vector
        vector = self.encode(text)

        # check blocklist usage in config
        if config('search','use_blocklist',bool):
            blocklist_path = install_path() + "/blocklist.txt"
            blocklist_text = ','.join(open(blocklist_path, 'r').read().splitlines()).strip(',')
        else:
            blocklist_text=""

        filter = self.get_context_filter(filter_text,blocklist_text)

        # Use `vector` for search for closest vectors in the collection
        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            query_filter=filter,  
            limit=150,  # max to safely fit in llama context
            search_params=SearchParams(hnsw_ef=128, exact=False),
        )
        documents = [result.payload['search'] for result in search_result if 'search' in result.payload]
        return documents
    
      
def search_prompts(q: str, filter_text: str, searcher: NeuralSearcher):
    return {"result": searcher.search(text=q, filter_text=filter_text)}

def print_results(documents, prompt_text, filter_text, page, items_per_page=5):
    if not documents or len(documents['result']) < 1:
        console.print("\nNo prompts found.\n", style=f"bold {search_color}")
    else:
        documents = documents['result']

        if filter_text:
            console.print(f"\nPrompt \\ Filter:", style=f"bold {search_color}")
            console.print(f"{prompt_text} \\ {filter_text}", style=f"{search_color}")
        else:
            console.print("\nPrompt:", style=f"bold {search_color}")
            console.print(prompt_text, style=f"{search_color}")

        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page

        document_count = len(documents)

        console.print(f"\n", style=f"bold {search_color}")
        
        for i, doc in enumerate(documents[start_index:end_index], start_index + 1):
            console.print(f"{i}. {doc}", style=f"{search_color}")
        
        console.print(f"\nPage {page} of {(document_count - 1) // items_per_page + 1}\n", style=f"bold {search_color}")

def result_check(documents): 
    # are there search results?
    try:
        len(documents['result'])
    except:
        console.print("\nYou have entered an EMPTY ROOM.\nThere are passages leading NOWHERE.\nAn ancient engraving reads:\n--try a /search first?\n", style=f"{error_color}")
        return False

    return True