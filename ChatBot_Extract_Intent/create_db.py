from langchain import FAISS
from langchain.document_loaders import PyPDFium2Loader
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import pypdfium2 as pdfium
from config_app.config import get_config
from download_and_load_index_data import download_and_index_pdf

config_app = get_config()
# embeddings = HuggingFaceEmbeddings(model_name=config_app["parameter"]["embeddings_name"],
#                                        model_kwargs={'device': 'cpu'})


session_urls = ['data/113_final_product.pdf']
# session_urls = ['data/product_detail.pdf']
faiss_index = download_and_index_pdf(session_urls)