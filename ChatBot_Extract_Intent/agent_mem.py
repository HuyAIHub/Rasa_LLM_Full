from langchain import LLMChain, OpenAI
from langchain.agents import AgentExecutor, Tool, ZeroShotAgent
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.agents import create_react_agent
from langchain import hub
import os

GROQ_API_KEY= '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'

import os

from groq import Groq

client = Groq(
    api_key=GROQ_API_KEY,
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama3-8b-8192",
)

print(chat_completion.choices[0].message.content)
def build_final_context(chunks):
    context = ""
    for index, chunk in enumerate(chunks):
        context += f"Context {index + 1}: " + chunk + "\n"
    return context

system_prompt = [
    '''
    Xin chào! Dạ, nồi áp suất là một lựa chọn tốt để nấu các món ăn ngon mà tiết kiệm thời gian. Trong tầm giá 1 triệu đồng, có một số sản phẩm nồi áp suất phổ biến và chất lượng mà bạn có thể xem xét:

    1. Nồi áp suất Midea: Một lựa chọn phổ biến với nhiều tính năng tiện ích và chất lượng đảm bảo.
    2. Nồi áp suất Sunhouse: Cũng là một lựa chọn phổ biến với nhiều dung tích khác nhau và tính năng an toàn.
    Nếu bạn cần thêm thông tin chi tiết về các sản phẩm hoặc muốn tìm kiếm mẫu nồi áp suất cụ thể, vui lòng cho biết thêm yêu cầu của bạn nhé. Tôi sẽ hỗ trợ bạn tìm kiếm sản phẩm phù hợp nhất trong tầm giá 1 triệu đồng.
    '''
]
context = build_final_context(system_prompt)

def qa(input=""):
    return '''
    HumanMessage:(content='hãy tư vấn giúp tôi sản phẩm bếp') 
    AIMessage: (content ='Dựa trên nhu cầu của bạn, tôi đề xuất một số sản phẩm như:    
        1. nồi điện kalite kl-301 1,7 lít 1850w           
        Giá tiền: 571780 VND
        2. nồi cơm điện, nồi cơm điện kalite kl-618, dung tích 1,8 lít 
        Giá tiền: 697070 VND
        3. nồi thủy tinh visions 2.25l vs-22/cl1       
        Giá tiền: 782540 VND
    Những sản phẩm này sẽ giúp bạn  hiệu quả và tiết kiệm thời gian. Có cần thêm thông tin chi tiết về sản phẩm nào không ạ?')
    HumanMessage:(content='nồi điện kalite')
    AIMessage: (content ='Dựa trên nhu cầu của bạn, tôi đề xuất một số sản phẩm như:    
        1. nồi điện kalite kl-301 1,7 lít 1850w           
        Giá tiền: 571780 VND'
    
    '''

tools = [
    Tool(
        name="QA System",
        func=qa,
        description="Useful for when you need to answer questions about the aspects asked. Input may be a partial or fully formed question. input should be product.",
    )   
]

conversational_memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=4, #Number of messages stored in memory
    return_messages=True #Must return the messages in the response.
)

suffix = """Begin!
    {chat_history}
    Question: {input}
    {agent_scratchpad}
"""
prefix = """Have a conversation with a human, answering the following questions as best you can based on the context and memory available.  
            All your answers must be in Vietnamese. 
            You have access to a single tool:"""

# prompt = ZeroShotAgent.create_prompt(
#     tools,
#     prefix=prefix,
#     suffix=suffix,  
#     input_variables=["input", "chat_history", "agent_scratchpad"],
# )
prompt = hub.pull("hwchase17/react-chat")
agent = create_react_agent(
    tools=tools,
    llm=llm,
    prompt=prompt,
)
# llm_chain = LLMChain(
#     llm=llm,
#     prompt=prompt,
# )

# agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)

agent_executor = AgentExecutor(agent=agent,
                               tools=tools,
                               verbose=True,
                               memory=conversational_memory,
                               max_iterations=30,
                               max_execution_time=300,
                               handle_parsing_errors=True
                               )

response = agent_executor.invoke({"input": "hãy tư vấn giúp tôi sản phẩm bếp"})
response = agent_executor.invoke({"input": "hãy tư vấn thông số sản phẩm Visions"})
print(response)

