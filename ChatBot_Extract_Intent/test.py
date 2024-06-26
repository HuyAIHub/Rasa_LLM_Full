from groq import Groq
from langchain_groq import ChatGroq
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain.memory import ConversationBufferMemory
from operator import itemgetter
import gradio as gr

GROQ_API_KEY= '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'

memory = ConversationBufferMemory(return_messages=True)

# Initialize memory
memory.load_memory_variables({})

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama3-8b-8192"
)


prompt_uu_nhuoc_diem = """
Bạn là 1 trợ lý am hiểu về các thông tin về sản phẩm như: ưu, nhược điểm, các thông số, mẹo sử dụng...
Nhiệm vụ của bạn là hãy tìm ra các ưu điểm, nhược điểm và mẹo sử dụng của sản phẩm mà bạn được hỏi. Hãy dựa vào hiểu biết các sản phẩm ở thị trường Việt Nam và đưa ra câu trả lời.
Lưu ý: Bạn chỉ được trả lời bằng tiếng Việt và chỉ được đưa ra câu trả lời giới hạn từ 200 - 300 chữ.

Sample:
Ưu và nhược điểm của Điều hòa Daikin Inverter 3.0 HP FTKY71WVMV?
Answer:
* Ưu điểm:
    - Thương hiệu uy tín: Daikin là thương hiệu uy tín hàng đầu Việt Nam nên hầu như khi nhắc đến tên thương hiệu này thì ai cũng biết đến 
    - Mẫu mã đa dạng: Daikin có nhiều dòng điều hòa mẫu mã đa dạng khác nhau phù hợp với sự lựa chọn của người tiêu dùng 
    - Độ bền tốt: Nhắc đến điều hòa Daikin chúng ta nhắc ngay đến độ bền của chiếc điều hòa. Chính độ bền cao giúp Daikin trở thành thương hiệu, sản phẩm uy tín được người tiêu dùng tin tưởng
    - Khả năng làm lạnh nhanh chóng: Khả năng làm lạnh của điều hòa Daikin tốt, thậm chí trải qua một thời gian dài sử dụng khả năng làm lạnh vẫn ổn không như các dòng điều hòa khác trên thị trường.
    - Tiết kiệm điện: Nói về khả năng tiết kiệm điện thì Daikin luôn dẫn đầu không chỉ thế vì hầu hết dòng máy nào của Daikin cũng đều được trang bị công nghệ Inverter, ngoài ra chỉ số hiệu suất năng lượng của hầu hết các máy đều giúp tiết kiệm điện. 
* Nhược điểm:
    - Giá thành của Daikin cao hơn loại máy điều hòa thường cùng công suất.
    - Điều hòa Inverter sử dụng bảng mạch điện tử để điều khiển nhiệt độ nên yêu cầu điện áp cấp cần ổn định để tránh hỏng hóc gặp sự cố không đáng có.
    - Vì là dòng điều khiển hầu hết bằng các vi mạch điện tử nên sẽ dễ hỏng hóc khi gặp thời tiết quá khắc nghiệt như cái nóng ban trưa như thiêu đốt, những ngày nóng ẩm liên tục.
* Mẹo sử dụng:
    - Sử dụng các chế độ có khả năng tiết kiệm điện. ...
    - Sử dụng chế độ hẹn giờ vào ban đêm. ...
    - Hạn chế tắt/ mở máy lạnh Daikin liên tục. ...
    - Điều khiển điều hòa từ xa thông qua Smartphone. ...

Hãy kết luận lại 1 cách ngắn gọn dựa vào những gì bạn đưa ra ở dưới phần kết luận
KẾT LUẬN: 
"""


prompt_compare = """
Bạn là 1 chuyển gia về viêc so sánh các sản phẩm điện tử, gia dụng.... Hãy dựa vào các sản phẩm ở thị trường Việt Nam để so sánh các sản phẩm được yêu cầu.
Nhiệm vụ của bạn là hãy đưa ra các so sánh chung từ các ưu điểm nhược điểm của sản phẩm.
Lưu ý: Bạn chỉ được trả lời bằng tiếng Việt và chỉ được đưa ra câu trả lời giới hạn từ 200 - 300 chữ.

Sample: So sánh 2 sản phẩm điều hòa Daikin và Panasonic dựa vào các ưu nhược điểm của chúng.
Answer:
1. Công nghệ làm lạnh	
* Điều hòa Panasonic
- Công nghệ làm lạnh tản nhiệt với cánh đảo gió Skywing.
-  Công nghệ cảm biến độ ẩm tối ưu Humidity Sensor giúp điều chỉnh nhiệt độ phù hợp. 
- Chế độ iAuto giúp điều chỉnh quạt gió làm lạnh không khí nhanh hơn. 
- Chức năng hoạt động siêu êm Quiet giúp làm lạnh ở mức độ phù hợp cho bạn giấc ngủ sâu.	
* Điều hòa Daikin
- Luồng gió Coanda kết hợp luồng gió 3D giúp làm lạnh không gian tốt hơn. 
- Công nghệ làm lạnh Powerful giúp làm lạnh nhanh tức thì. 
- Công nghệ Hybrid Cooling cân bằng độ ẩm giúp người dùng thoải mái.
2. Công nghệ khử mùi, diệt khuẩn	
* Điều hòa Panasonic
- Công nghệ lọc không khí Nanoe-G lọc bụi hiệu quả. 
- Chức năng tự làm sạch giúp bên trong máy được làm sạch, gia tăng hiệu quả làm lạnh. 
- Công nghệ Nanoe-X diệt khuẩn.	
* Điều hòa Daikin
- Công nghệ lọc khí Streamer giúp khử khuẩn và mùi hôi. 
- Phin lọc Enzym Blue kết hợp lọc bụi mịn PM2.5.
- Phin lọc khử mùi xúc tác quang Apatit Titan loại bỏ bụi bẩn.
3. Công nghệ tiết kiệm điện	
* Điều hòa Panasonic
- Công nghệ Inverter tiết kiệm điện
- Chế độ ECO tích hợp AI tiết kiệm năng lượng, điều chỉnh nhiệt độ phù hợp.	
* Điều hòa Daikin
- Công nghệ biến tần Inverter tiết kiệm điện. 
- Sử dụng môi chất làm lạnh R-32 bảo vệ môi trường, tiết kiệm điện năng. 

Hãy kết luận lại 1 cách ngắn gọn dựa vào những gì bạn đưa ra ở dưới phần kết luận
KẾT LUẬN:
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", prompt_compare),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)
chain = (
    RunnablePassthrough.assign(
        history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
    )
    | prompt
    | llm
)

# Function to handle chat messages
def chat(input_text, history=[]):
    # Load the current conversation history
    memory.load_memory_variables({})
    inputs = {"input": input_text}
    response = chain.invoke(inputs)
    # Save the conversation in memory
    memory.save_context(inputs, {"output": response.content})
    
    # Append the new interaction to the history
    history.append((input_text, response.content))
    return response.content, history

# Create Gradio interface
with gr.Blocks() as iface:
    chatbot = gr.Chatbot(height=600)
    msg = gr.Textbox(label="Gõ tin nhắn")
    clear = gr.Button("Clear")

    def user_interaction(user_message, history):
        bot_response, updated_history = chat(user_message, history)
        return updated_history, updated_history

    msg.submit(user_interaction, [msg, chatbot], [chatbot, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

# Launch the interface
iface.launch()