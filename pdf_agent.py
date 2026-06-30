from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class PDFAgent:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.text_chunks = []

    def load_pdf(self, file):
        reader = PdfReader(file)
        text = ""

        for page in reader.pages:
            text += page.extract_text() + "\n"

        # Split into chunks
        self.text_chunks = [text[i:i+500] for i in range(0, len(text), 500)]

        # Create embeddings
        embeddings = self.model.encode(self.text_chunks)

        self.index = faiss.IndexFlatL2(384)
        self.index.add(np.array(embeddings))

        return "PDF loaded successfully!"

    def query(self, question):
        if self.index is None:
            return "Please upload a PDF first."

        q_embedding = self.model.encode([question])
        D, I = self.index.search(np.array(q_embedding), k=2)

        results = [self.text_chunks[i] for i in I[0]]

        return "\n\n".join(results)