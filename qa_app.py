import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from ui_template import css, user_template, bot_template
from langchain.prompts import PromptTemplate
import docx2txt


def get_text_from_docs(docs):
    """
    Read multiple documents in different file formats. Acceptable formats are .pdf, .docx and .txt
    """
    text_str =""
    for d in docs:
        text_fpath = "./src_data/"+d.name
        if d.name.endswith(".pdf"):
            doc_reader = PdfReader(text_fpath)
            for page in doc_reader.pages:
                text_str += page.extract_text()

        elif d.name.endswith(".txt"):
            with open(text_fpath,"rt") as f:
                text_str += f.read()

        elif d.name.endswith(".docx"):
            text_str += docx2txt.process(text_fpath)

        else:
            st.write("Unable to process your document files.  Only .pdf .docx and .txt file format are allowed.")

    return text_str

def get_text_from_pdf(docs):
    """
    Read pdf documents page by page and append all pages in one concatnated string.
    """
    text_str =""
    for d in docs:
        doc_reader = PdfReader(d)
        for page in doc_reader.pages:
            text_str += page.extract_text()
    return text_str

def get_text_by_chunks(text):
    """
    split the text str into chunk_size
    """
    text_splitter = CharacterTextSplitter(
                                separator="\n",
                                chunk_size = 3000,
                                chunk_overlap=100,
                                length_function=len
                    )
    chunks = text_splitter.split_text(text)
    return chunks

def create_vectorstores(text_chunks):
    embeddings = OpenAIEmbeddings() #HuggingFaceInstructorEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstores = FAISS.from_texts(texts=text_chunks,embedding=embeddings)
    return vectorstores

def create_conversation_chain(vs):
    custom_prompt_template = """ Use the following pieces of context to answer the question at the end.  If you don't know the answer, just say that you don't know, don't try to make up an answer. 
                                 {context}

                                 Question: {question}
                                 Answer:"""
    PROMPT = PromptTemplate(
                    template=custom_prompt_template, input_variables=["context","question"]
            )
    
    llm = ChatOpenAI(model= "gpt-3.5-turbo",temperature=0)
    memory = ConversationBufferMemory(memory_key="chat_history",return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
                                            llm = llm,
                                            retriever= vs.as_retriever(search_type="mmr"),  ## search_type="similarity" # search_kwargs={"k":1}
                                            combine_docs_chain_kwargs={"prompt":PROMPT},
                                            memory=memory
                        )
    return conversation_chain

def process_user_question(user_question):
    response = st.session_state.conver({'question':user_question})
    st.session_state.chat_history = response['chat_history']

    for i,message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}",message.content), unsafe_allow_html=True)

        else:
            st.write(bot_template.replace("{{MSG}}",message.content),unsafe_allow_html=True)

def run_qa_app():
    load_dotenv()
    st.set_page_config(page_title="Chat with AI Bot",page_icon=":books:", layout='centered')

    st.write(css,unsafe_allow_html=True)

    if "conver" not in st.session_state:
        st.session_state.conver = None
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    
    st.header("Chat with AI Bot :robot_face:")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        process_user_question(user_question)

    # st.write(user_template.replace("{{MSG}}","Hello AI Bot"), unsafe_allow_html=True)
    # st.write(user_template.replace("{{MSG}}","Hello User"), unsafe_allow_html=True)

    with st.sidebar:
        st.subheader("Your Documents :books:")
        docs = st.file_uploader("Upload document files (.pdf, .txt, .docx) and click on 'Process'",accept_multiple_files=True)

        if st.button("Process"):
            with st.spinner("Processing documents"):

                # get raw text from only pdf docs
                # raw_text = get_text_from_pdf(docs)

                # get raw text from multiple file format docs (.txt, .pdf and .docx)
                raw_text = get_text_from_docs(docs)

                # get text chunks
                text_chunks = get_text_by_chunks(raw_text)
                
                # create vector store using embedding model
                vs = create_vectorstores(text_chunks)

                # create conversation chain
                # and make conver variable persistent by using streamlit session state (i.e., prvent streamlit re-running/re-loading that variable in one active session)
                # streamlit normally reload/rerun entire code whenever it detects an event (such as clicking a button, enter text etc)
                st.session_state.conver = create_conversation_chain(vs)


if __name__ == "__main__":
    run_qa_app()