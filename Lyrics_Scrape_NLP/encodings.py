from sentence_transformers import SentenceTransformer
import torch
from torch.nn import CosineSimilarity

class TextEncoder:
    def __init__(self):
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cuda")
    
    def compare(self, sentence1, sentence2):
        embeddings = self.model.encode([sentence1, sentence2])
        cos = CosineSimilarity(dim=1)

        return cos(torch.from_numpy(embeddings[0]).unsqueeze(0), torch.from_numpy(embeddings[1]).unsqueeze(0)).item()
    
    def encode(self, sentence):
        return self.model.encode(sentence)
    
if __name__ == "__main__":
    pass