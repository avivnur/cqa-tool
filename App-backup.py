import streamlit as st
import openai
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import FunctionCallingAgentWorker, AgentRunner
from llama_index.core.objects import ObjectIndex
import openai
import tempfile
import os
import uuid
import gc
from utils import pdf_processing, process_inquiry_and_show_latest_image, display_pdf, bar_chart_tool, line_chart_tool

openai.api_key = st.secrets.openai_key
st.set_page_config(
    page_title="CQA",
    page_icon="💻",
    layout="wide",
)

st.title("📊 Chart Question Answering Tool")

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

session_id = st.session_state.id
client = None

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    st.session_state.file_cache = {}
    gc.collect()

if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question!"}
    ]

# Add dropdown on the side bar to choose the model
model = st.sidebar.selectbox(
    "Select a model",
    ["gpt-3.5-turbo", "gpt-4","gpt-4-turbo"],
    index=0,
)

# Setup Generalist Agent here
llm = OpenAI(model=model, temperature=0.5)
query_tools = [bar_chart_tool, line_chart_tool]  # Example tools for handling queries
obj_index = ObjectIndex.from_objects(query_tools, index_cls=VectorStoreIndex)
agent_worker = FunctionCallingAgentWorker.from_tools(tool_retriever=obj_index.as_retriever(similarity_top_k=5), llm=llm, verbose=True, allow_parallel_tool_calls=True)
agent = AgentRunner(agent_worker)

# Add PDF file uploader
with st.sidebar:
    st.header("Upload a PDF file")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    if uploaded_file:
        try:
            index_loaded = False
            try:
                storage_context = StorageContext.from_defaults(persist_dir="./test_files/textdata")
                text_index = load_index_from_storage(storage_context)
                storage_context = StorageContext.from_defaults(persist_dir="./test_files/chartdata")
                chart_index = load_index_from_storage(storage_context)
                index_loaded = True
            except:
                index_loaded = False

            if not index_loaded:
                with tempfile.TemporaryDirectory() as temp_dir:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    file_key = f"{session_id}-{uploaded_file.name}"
                    st.write("Processing your document...")
                    st.spinner()
                    text_docs, chart_docs = pdf_processing(file_path)
                    text_index = VectorStoreIndex.from_documents(text_docs)
                    chart_index = VectorStoreIndex.from_documents(chart_docs)

            # Continue with loading or creating indices and objects
            # Assume that the rest of the processing is similar regardless of the source of the indices
            text_engine = text_index.as_query_engine(streaming=True)
            chart_engine = chart_index.as_query_engine(streaming=True)
            query_engine_tools = [
                QueryEngineTool(query_engine=text_engine, metadata=ToolMetadata(name="text_engine", description="Provides information about text in the document.")),
                QueryEngineTool(query_engine=chart_engine, metadata=ToolMetadata(name="chart_engine", description="Provides information about chart data in the document.")),
                bar_chart_tool, line_chart_tool
            ]
            obj_index = ObjectIndex.from_objects(query_engine_tools, index_cls=VectorStoreIndex)
            agent_worker = FunctionCallingAgentWorker.from_tools(tool_retriever=obj_index.as_retriever(similarity_top_k=5), llm=llm, verbose=True, allow_parallel_tool_calls=True)
            agent = AgentRunner(agent_worker)
            st.session_state.file_cache[uploaded_file.name] = (text_engine, chart_engine, agent)
            st.success("Done! Ask me a question about the document.")
                
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()
        # try:
            # with tempfile.TemporaryDirectory() as temp_dir:
            #     file_path = os.path.join(temp_dir, uploaded_file.name)

            #     with open(file_path, "wb") as f:
            #         f.write(uploaded_file.getvalue())
            #     file_key = f"{session_id}-{uploaded_file.name}"
            #     st.write("Indexing your document...")
            #     st.spinner()
            #     # st.write(file_path)
            #     # st.write(file_key)

            #     if file_key not in st.session_state.get('file_cache', {}):
            #         if os.path.exists(file_path):
            #             text_docs, chart_docs = pdf_processing(file_path)
            #         else:
            #             st.error("Could not find the uploaded file.")
            #             st.stop()

            #         text_index = VectorStoreIndex.from_documents(text_docs)
            #         chart_index = VectorStoreIndex.from_documents(chart_docs)

        #     index_loaded = False
        #     try:
        #         storage_context = StorageContext.from_defaults(persist_dir="./test_files/textdata")
        #         text_index = load_index_from_storage(storage_context)
        #         storage_context = StorageContext.from_defaults(persist_dir="./test_files/chartdata")
        #         chart_index = load_index_from_storage(storage_context)
        #         index_loaded = True
        #     except:
        #         index_loaded = False

        #     if not index_loaded:
        #         with tempfile.TemporaryDirectory() as temp_dir:
        #             file_path = os.path.join(temp_dir, uploaded_file.name)
        #             with open(file_path, "wb") as f:
        #                 f.write(uploaded_file.getvalue())
        #             file_key = f"{session_id}-{uploaded_file.name}"
        #             st.write("Processing your document...")
        #             st.spinner()
        #             text_docs, chart_docs = pdf_processing(file_path)
        #             text_index = VectorStoreIndex.from_documents(text_docs)
        #             chart_index = VectorStoreIndex.from_documents(chart_docs)
        #     text_engine = text_index.as_query_engine(streaming=True)
        #     chart_engine = chart_index.as_query_engine(streaming=True)

        #     query_engine_tools = [
        #         QueryEngineTool(
        #             query_engine=text_engine,
        #             metadata=ToolMetadata(
        #                 name="text_engine",
        #                 description=(
        #                     "Provides information about text in the document. "
        #                     "Use a detailed plain text question as input to the tool."
        #                     "Do not hallucinate or make up any information."
        #                 ),
        #             ),
        #         ),
        #         QueryEngineTool(
        #             query_engine=chart_engine,
        #             metadata=ToolMetadata(
        #                 name="chart_engine",
        #                 description=(
        #                     "Provides information about chart data in the document."
        #                     "Use a detailed plain text question as input to the tool."
        #                     "Do not hallucinate or make up any information."
        #                 )
        #             ),
        #         ),
        #         bar_chart_tool,
        #         line_chart_tool,
        #     ]

        #     obj_index = ObjectIndex.from_objects(
        #         query_engine_tools,
        #         index_cls=VectorStoreIndex,
        #     )

        #     llm = OpenAI(
        #         model=model,
        #         temperature=0.5,
        #         system_prompt="You are a data analyst working with a document that contains text and chart data provided.\
        #             You need to answer questions and generate insights based on the information in the document.\
        #             Do not provide any information that is not present in the document.\
        #             Do not hallucinate or make up any information."
        #     )

        #     agent_worker = FunctionCallingAgentWorker.from_tools(
        #         tool_retriever=obj_index.as_retriever(similarity_top_k=5),
        #         llm=llm,
        #         verbose=True,
        #         allow_parallel_tool_calls=True,
        #     )
            
        #     agent = AgentRunner(agent_worker)
            
        #     st.session_state.file_cache[file_key] = (text_engine, chart_engine, agent)
        # else:
        #     text_engine, chart_engine, agent = st.session_state.file_cache[file_key]

        #         st.success("Done! Ask me a question about the document.")
        #         with st.expander("📈 PDF Preview"):
        #             display_pdf(uploaded_file)

        # except Exception as e:
        #     st.error(e)
        #     st.stop()
# add a reset button on the sidebar
if st.sidebar.button("Reset"):
    reset_chat()

if uploaded_file:
    with st.expander("📈 PDF Preview"):
        display_pdf(uploaded_file)

# # Function to display conversation history
# def display_conversation_history():
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

# # Function to send messages and process responses
# def send_message(prompt):
#     if prompt:
#         # Add user message to chat history
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         # Display user message in chat message container
#         with st.chat_message("user"):
#             st.markdown(prompt)

#         # Generate a response using the agent, which might include generating an image
#         latest_img_path = process_inquiry_and_show_latest_image(prompt, agent)
#         if latest_img_path:
#             with st.chat_message("assistant"):
#                 st.image(latest_img_path)

#         # Generate text response using the agent
#         full_response = agent.chat(prompt)
#         with st.chat_message("assistant"):
#             st.markdown(full_response)

#         # Add assistant response to chat history
#         st.session_state.messages.append({"role": "assistant", "content": full_response})

# # Display conversation history first
# display_conversation_history()

# # Accept user input and provide a send message functionality
# if prompt := st.chat_input("What do you have in mind?"):
#     send_message(prompt)

# Pre-create containers for chat display to manage dynamic content better
chat_container = st.container()

# Function to send messages and process responses
def send_message(prompt):
    if prompt:
        # Add user message to chat history and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        # Process the inquiry, possibly generating an image
        latest_img_path = process_inquiry_and_show_latest_image(prompt, agent)
        if latest_img_path:
            with chat_container.chat_message("assistant"):
                st.image(latest_img_path)

        # Generate text response using the agent
        full_response = agent.chat(prompt)
        with chat_container.chat_message("assistant"):
            st.markdown(full_response)

        # Append the assistant's response to the chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Initialize or update the conversation history in the app
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Function to initialize or refresh conversation history
def display_conversation_history():
    # Using a container to manage the dynamic display of messages
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# Display all previous parts of the conversation when the page is (re)loaded
display_conversation_history()

# Accept user input and provide a send message functionality
if prompt := st.chat_input("What do you have in mind?"):
    send_message(prompt)