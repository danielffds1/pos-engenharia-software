import os
import time

from dotenv import load_dotenv
from google.api_core.exceptions import ResourceExhausted
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from store import get_vector_store

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")

# Free tier do Gemini limita tokens de embedding por minuto, então enviamos
# os chunks em lotes pequenos com uma pausa entre eles.
BATCH_SIZE = 10
BATCH_DELAY_SECONDS = 5


@retry(
    retry=retry_if_exception_type(ResourceExhausted),
    wait=wait_exponential(multiplier=1, min=20, max=60),
    stop=stop_after_attempt(5),
)
def _add_documents_with_retry(vector_store, batch):
    vector_store.add_documents(batch)


def ingest_pdf():
    documents = PyPDFLoader(PDF_PATH).load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)

    vector_store = get_vector_store()
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        _add_documents_with_retry(vector_store, batch)
        print(f"  lote {i // BATCH_SIZE + 1}: {len(batch)} chunks ingeridos")
        if i + BATCH_SIZE < len(chunks):
            time.sleep(BATCH_DELAY_SECONDS)

    print(f"Ingestão concluída: {len(chunks)} chunks armazenados.")


if __name__ == "__main__":
    ingest_pdf()
