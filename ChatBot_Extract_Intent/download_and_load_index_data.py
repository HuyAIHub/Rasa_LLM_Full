from langchain import FAISS
from langchain.document_loaders import PyPDFium2Loader
from langchain_community.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import pypdfium2 as pdfium
from ChatBot_Extract_Intent.config_app.config import get_config

config_app = get_config()

embeddings = OpenAIEmbeddings(openai_api_key=config_app["parameter"]["openai_api_key"])

def download_and_index_pdf(urls: list[str]) -> FAISS:
    """
    Download and index a list of PDFs based on the URLs
    """

    def __update_metadata(pages, url):
        """
        Add to the document metadata the title and original URL
        """
        for page in pages:
            pdf = pdfium.PdfDocument(page.metadata['source'])
            title = pdf.get_metadata_dict().get('Title', url)
            page.metadata['source'] = url
            page.metadata['title'] = title
        return pages

    all_pages = []
    for url in urls:
        loader = PyPDFium2Loader(url)
        splitter = CharacterTextSplitter(chunk_size=config_app["parameter"]["chunk_size"], chunk_overlap=config_app["parameter"]["chunk_overlap"])
        pages = loader.load_and_split(splitter)
        pages = __update_metadata(pages, url)
        all_pages += pages

    faiss_index = FAISS.from_documents(all_pages, embeddings)
    faiss_index.save_local(config_app["parameter"]["DB_FAISS_PATH"])
    print('save db successfully!')
    return faiss_index


def load_and_index_pdf():
    db = FAISS.load_local(config_app["parameter"]["DB_FAISS_PATH"], embeddings,allow_dangerous_deserialization = True)
    print('load_index_done!')
    return db

def search_faiss_index(faiss_index: FAISS, query: str, top_k: int = 3) -> list:
    """
    Search a FAISS index, using the passed query
    """
    docs = faiss_index.similarity_search(query, k=top_k)
    return docs
