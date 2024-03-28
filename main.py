from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharactertextSplitter
from langchain.llms import CTransformers
from src.helper import *

# Load the PDF File
loader=DirectoryLoader('data/',
                       glob="*.pdf",
                       loader_cls=PyPDFLoader)

documents=loader.load()

# Split Text into chunks
text_splitter=RecursiveCharactertextSplitter(chunk_size=500,
                                             chuck_overlap=50)
text_chunks=text_splitter.split_documents(documents)

#Load the Embedding Model
embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',
                                model_kwargs={'device':'cpu'})

#Convert the Text chunks into Embeddings and create a FAISS Vector Store
vector_store=FAISS.from_documents(text_chunks, embeddings)

llm = CTransformers(model='model/llama-2-7b-chat.ggmlv3.q4_0.bin',
                    model_type = 'llama',
                    config={'max_new_tokens': 128,
                            'temperature': 0.01}
                     )

qa_prompt=PromptTemplate(template=template, input_variables=['context','question'])

chain = RetrievalQA.from_chain_type(llm=llm,
                                    
                                    chain_type='stuff',
                                    retreiver=vector_store.as_retriever(search_kwargs={'k':2}),
                                    return_source_documents=True,
                                    chain_type_kwargs={'prompt': qa_prompt})