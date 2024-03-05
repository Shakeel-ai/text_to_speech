import streamlit as st
from langchain.document_loaders import YoutubeLoader
from pytube import YouTube
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from PyPDF2 import PdfReader
import docx
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import BeautifulSoupTransformer
import os
from urllib.parse import urlparse
from openai import OpenAI
from googletrans import Translator
openai_api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="M. Shakeel")
st.title("Text To Speech App")
#make openai client
client = OpenAI(api_key=openai_api_key)

def main():

    uploaded_files = st.file_uploader("Upload Your File",type=["pdf","docs","html"],accept_multiple_files = True)
    url = st.text_input("Enter Youtube Video Url Or Website Url")
    text_input = st.text_input("Enter Text")
    if st.button("Click To Start"):
  
        if url:
            try:
                if is_youtube_url(url):  
                    text = get_video_text(url)
                    y_file_name = get_video_title(url)
                    if text:
                        chunks = get_text_chunks(text)
                        for chunk in chunks:
                            ur_text = translator(chunk)
                            y_file_name = "yotube"
                            generate_speech(text=ur_text,file_name=y_file_name)
                        audio_file = open(f"{y_file_name}.mp3","rb")
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes)
                else:
                    text = get_web_text(url) 
                    #w_file_name = get_website_title(url)
                    if text:
                        chunks = get_text_chunks(text)
                        w_file_name = "website"
                        for chunk in chunks:
                            ur_text = translator(chunk)
                            generate_speech(text=ur_text,file_name=w_file_name)
                        audio_file = open(f"{w_file_name}.mp3","rb")
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes)
            except Exception as e:
                st.write(f"Error: {e}")   
            
        if uploaded_files:
            try:         
                for uploaded_file in uploaded_files:
                    f_file_name = uploaded_file.name
                    text = get_files_text(uploaded_file)
                    if text:
                        chunks = get_text_chunks(text)
                        for chunk in chunks:
                            ur_text = translator(chunk)
                            generate_speech(ur_text,f_file_name)
                        audio_file = open(f"{f_file_name}.mp3","rb")
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes)
                  
            except Exception as e:
                st.write(f"Error: {e}")  
            
        if text_input:
            file_name="given_text"
            if st.button("Translate"):
                ur_text = translator(text_input)
                generate_speech(ur_text,file_name=file_name)
            else:
                generate_speech(text_input,file_name=file_name)

            audio_file = open(f"{file_name}.mp3","rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes)
        
def get_files_text(uploaded_file):
    text = ""
    split_tup = os.path.splitext(uploaded_file.name)
    file_extension = split_tup[1]
    if file_extension == ".pdf":
        text+=get_pdf_text(uploaded_file)
    elif file_extension == ".docs":
        text+=get_docx_text(uploaded_file)
    elif file_extension == ".html":
        text+=get_html_text(uploaded_file)    
    else:
        pass
    return text

def get_pdf_text(pdf):
    text = ""   
    pdf_reader = PdfReader(pdf)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_docx_text(file):
    doc = docx.document(file)
    all_text = []
    for docpara in doc.paragraphs:
        all_text+=docpara.append(docpara)
        text = ''.join(all_text)
    return text   

def get_html_text(html):
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
    html,tags_to_extract=["p","li","div"]
    )
    text = docs_transformed[0].page_content
    return text 
   
def get_video_text(url):
    loader = YoutubeLoader.from_youtube_url(url)
    pages = loader.load()
    text = pages[0].page_content
    return text
def get_video_title(url):
    yt = YouTube(url)
    title = yt.title
    return title
   
def is_youtube_url(url):
    parsed_url = urlparse(url)
    return "youtube.com" in parsed_url.netloc or "youtu.be" in parsed_url.netloc

def get_web_text(url):
    loader = AsyncHtmlLoader([url])
    html = loader.load()
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        html,tags_to_extract=["p","li","div"]
    )
    text = docs_transformed[0].page_content
    return text

def get_website_title(url):
    parsed_url = urlparse(url)
    website_name = parsed_url.netloc
    return website_name

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="",
        chunk_size = 500,
        length_function = len,
        is_separator_regex=True
    )
    chunks = text_splitter.split_text(text)
    return chunks
    

def generate_speech(text,file_name):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    file_path = f"{file_name}.mp3"
    response.stream_to_file(file_path)

def translator(text):
    translator = Translator()
    response = translator.translate(text,src="en",dest="ur")
    return response



if __name__ == '__main__':
    main()
    