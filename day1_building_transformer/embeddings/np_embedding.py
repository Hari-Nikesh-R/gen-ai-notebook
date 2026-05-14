import os
import sys
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tokenizer.tokenizer import Tokenizer

# Add the parent directory (day1_building_transformer) to Python's module search path



class Embedding:
    def __init__(self, vocab_size, embedding_dim):
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.embedding_matrix = np.random.randn(vocab_size, embedding_dim)
    
    def embed(self, token_ids):
        return self.embedding_matrix[token_ids]
    
    def embeded_matrix(self):
        return self.embedding_matrix


token = Tokenizer(["i love pen", "i love ai"])
vocab_size = len(token.vocab)
embedding_dim = 4 

embedding = Embedding(vocab_size, embedding_dim)
print(embedding.embeded_matrix())
print()
print("============")
print()
encoded_sentence = token.encoding()
print(embedding.embed(encoded_sentence))
