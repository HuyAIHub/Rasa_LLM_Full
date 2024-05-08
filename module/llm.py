import os
from langchain import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory, CombinedMemory, VectorStoreRetrieverMemory
from langchain import PromptTemplate
from ChatBot_Extract_Intent.download_and_load_index_data import search_faiss_index
from ChatBot_Extract_Intent.config_app.config import get_config

config_app = get_config()

class SnippetsBufferWindowMemory(ConversationBufferWindowMemory):
    """
    MemoryBuffer được sử dụng để giữ các đoạn tài liệu. Kế thừa từ ConversationBufferWindowMemory và ghi đè lên
    phương thức Load_memory_variables
    """

    index: FAISS = None
    pages: list = []
    memory_key = 'snippets'
    snippets: list = []

    def __init__(self, *args, **kwargs):
        ConversationBufferWindowMemory.__init__(self, *args, **kwargs)
        self.index = kwargs['index']

    def load_memory_variables(self, inputs) -> dict:
        """
        Dựa trên thông tin đầu vào của người dùng, hãy tìm kiếm chỉ mục và thêm các đoạn mã tương tự vào bộ nhớ 
        (nhưng chỉ khi chúng chưa có trong bộ nhớ)
        """
        # try:
        # Search snippets
        similar_snippets = search_faiss_index(self.index, inputs['user_messages_history'], config_app["parameter"]["number_snippets_to_retrieve"])
        # In order to respect the buffer size and make its pruning work, need to reverse the list, and then un-reverse it later
        # This way, the most relevant snippets are kept at the start of the list
        self.snippets = [snippet for snippet in reversed(self.snippets)]
        self.pages = [page for page in reversed(self.pages)]

        for snippet in similar_snippets:
            page_number = snippet.metadata['page']
            # Load into memory only new snippets
            snippet_to_add = f"The following snippet was extracted from the following document: "
            if snippet.metadata['title'] == snippet.metadata['source']:
                snippet_to_add += f"{snippet.metadata['source']}\n"
            else:
                snippet_to_add += f"[{snippet.metadata['title']}]({snippet.metadata['source']})\n"

            snippet_to_add += f"<START_SNIPPET_PAGE_{page_number + 1}>\n"
            snippet_to_add += f"{snippet.page_content}\n"
            snippet_to_add += f"<END_SNIPPET_PAGE_{page_number + 1}>\n"
            if snippet_to_add not in self.snippets:
                self.pages.append(page_number)
                self.snippets.append(snippet_to_add)

        # Reverse list of snippets and pages, in order to keep the most relevant at the top
        # Also prune the list to keep the buffer within the define size (k)
        self.snippets = [snippet for snippet in reversed(self.snippets)][:self.k]
        self.pages = [page for page in reversed(self.pages)][:self.k]
        to_return = ''.join(self.snippets)

        return {'snippets': to_return}
        # except: return {'snippets': ""}

def construct_conversation(prompt: str, llm, memory) -> ConversationChain:
    """
    Construct a ConversationChain object
    """

    prompt = PromptTemplate.from_template(
        template=prompt,
    )

    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False,
        prompt=prompt
    )
    return conversation


def initialize_chat_conversation(index: FAISS,
                                 model_to_use, conv_memory, snippets_memory) -> ConversationChain:
    '''
     prompt_header = """You are an expert, tasked with helping customers with their questions. They will ask you questions and provide technical snippets that may or may not contain the answer, and it's your job to find the answer if possible, while taking into account the entire conversation context.
    The following snippets can be used to help you answer the questions:    
    {snippets}    
    The following is a friendly conversation between a customer and you. Please answer the customer's needs based on the provided snippets and the conversation history. Make sure to take the previous messages in consideration, as they contain additional context.
    If the provided snippets don't include the answer, please say so, and don't try to make up an answer instead. Include in your reply the title of the document and the page from where your answer is coming from, if applicable.
    You may only respond to the information contained in the document. If the question is about product price, please answer:"Thông tin về giá sản phẩm xin mời bạn liên hệ với bộ phận bán hàng" .
    The number of product codes is the number of products in the category. Be careful not to put document information in your answer.All your answers must be in Vietnamese. 

    {history}    
    Customer: {input}
    """
    '''
    prompt_header = """You are an expert, assigned to help look up information about products. They will ask you questions and provide technical passages that may or may not contain answers, and your task is to find the answer if possible within the knowledge base you are given, while taking into account entire conversation context.
    The following paragraphs can be used to help you answer the questions:    
    {snippets}    
    The following is a friendly conversation between a customer and you. Please respond to customer needs based on the provided snippets and conversation history. Be sure to review previous messages as they contain additional context.
    If the snippet provided does not include an answer, please say so and don't try to create an answer instead. The question will usually ask about the quantity and details of the product. You answer the exact focus of the question.
    You can only respond to the information contained in the document. If the question is about information that does not exist in the document, you must not make up the answer or use information from another product to answer. If you have a question about product price, please answer: "For product price information, please contact the sales department for more detailed information." .
    Be careful not to mistakenly include information from the document in your answer. All your answers must be in Vietnamese.

    {history}    
    Customer: {input}
    """

    os.environ['OPENAI_API_KEY'] = config_app["parameter"]["openai_api_key"]
    llm = ChatOpenAI(model_name=model_to_use, temperature=config_app["parameter"]["temperature"])
    if conv_memory == [] and snippets_memory == []:
        conv_memory = ConversationBufferWindowMemory(k=config_app["parameter"]["search_number_messages"], input_key="input")
        snippets_memory = SnippetsBufferWindowMemory(k=config_app["parameter"]["prompt_number_snippets"], index=index, 
                                                    memory_key='snippets', input_key="snippets")
    else:
        conv_memory = ConversationBufferWindowMemory(k=config_app["parameter"]["search_number_messages"], input_key="input", chat_memory=conv_memory)
        snippets_memory = SnippetsBufferWindowMemory(k=config_app["parameter"]["prompt_number_snippets"], index=index, 
                                                    memory_key='snippets', input_key="snippets", chat_memory=snippets_memory)
    memory = CombinedMemory(memories=[conv_memory, snippets_memory])
    conversation = construct_conversation(prompt_header, llm, memory)

    return conversation, conv_memory