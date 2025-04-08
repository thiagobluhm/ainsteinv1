from langchain_core.messages import AIMessage, HumanMessage
import streamlit as st
import requests
import hashlib
from datetime import datetime
import tempfile
from pathlib import Path
import base64
import re
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(layout="wide", page_title="AIstein - Assistente Digital", page_icon="🤖")
os.chdir(os.path.abspath(os.curdir))

API_URL = "https://appaistein-dnaxg3amcthxecfs.eastus2-01.azurewebsites.net/aistein/"

from azure.storage.blob import BlobServiceClient
import uuid

def data_legivel():
    data_legivel = datetime.fromtimestamp(datetime.timestamp(datetime.now())).strftime('%Y-%m-%d %H:%M:%S')
    return data_legivel, f"Data e hora do início da conversa: {data_legivel}"

def conversaID():
    datalegivel, _ = data_legivel()
    return hashlib.sha256(datalegivel.encode('utf-8')).hexdigest()[1:]

def upload_file_to_blob(file_path, blob_name=None):
    try:
        blob_name = blob_name or f"{uuid.uuid4()}{Path(file_path).suffix}"
        container_name = "chatwpp"
        connection_string = os.environ.get("META_CONN_STRING")

        storage_account_url = "https://bluhmstorage.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=connection_string)
        blob_client = blob_service_client.get_container_client(container_name).get_blob_client(blob_name)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        return blob_name
    except Exception as e:
        st.error(f"Erro ao subir para o Blob: {e}")
        return None

def save_uploaded_file(uploaded_file):
    file_extension = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_file.write(uploaded_file.read())
        return temp_file.name

def serializar_chat_history(chat_history):
    serializado = []
    for message in chat_history:
        if isinstance(message, HumanMessage):
            serializado.append({"role": "user", "content": message.content})
        elif isinstance(message, AIMessage):
            serializado.append({"role": "assistant", "content": message.content})
    return serializado

def enviar_prompt_api(prompt, session_id, chat_history):
    try:
        chat_history_serializado = serializar_chat_history(chat_history)
        response = requests.post(
            API_URL,
            headers={'Content-Type': 'application/json'},
            json={"prompt": prompt, "session_id": session_id, "chat_history": chat_history_serializado},
            timeout=300,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"resposta": "Erro na API", "chat_history": chat_history}
    except Exception as e:
        return {"resposta": f"Erro inesperado: {e}", "chat_history": chat_history}

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.image('https://grupoportfolio.com.br/portfolio-formacao/wp-content/uploads/sites/2/2020/09/portfolio-tech-negativo-2.png', use_container_width="auto")
    uploaded_file = st.file_uploader("Selecione um arquivo", type=["txt", "pdf", "jpg", "png", "csv"])

if "hash_id" not in st.session_state:
    st.session_state["hash_id"] = conversaID()
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, meu nome é AIstein, sou um assistente digital e vou te auxiliar."}]
if "arquivo_processado" not in st.session_state:
    st.session_state["arquivo_processado"] = False

st.title("\U0001F5E8\uFE0F Assistente Digital - AIstein2")

for msg in st.session_state.messages:
    st.chat_message(msg["role"], avatar="👤").write(msg["content"])

# Processamento de arquivo e controle
file_name = None
if uploaded_file and not st.session_state.arquivo_processado:
    local_path = save_uploaded_file(uploaded_file)
    file_name = upload_file_to_blob(local_path)
    st.session_state.arquivo_processado = True
    st.rerun()

chat_input = st.chat_input(placeholder="Digite aqui o que precisa...")
prompt = chat_input if chat_input else file_name

if prompt:
    if prompt == file_name:
        conteudo = f"Arquivo carregado: {file_name}"
        st.chat_message("user", avatar="🤓").write(conteudo)
    else:
        conteudo = prompt
        st.chat_message("user", avatar="🤓").write(prompt)

    st.session_state.messages.append({"role": "user", "content": conteudo})
    st.session_state.chat_history.append(HumanMessage(content=conteudo))

    with st.spinner("O assistente está processando sua solicitação..."):
        response = enviar_prompt_api(prompt, st.session_state.hash_id, st.session_state.chat_history)
        resposta = response.get("resposta", "⚠️ Nenhuma resposta recebida da API.")

        if not isinstance(resposta, str):
            resposta = str(resposta)

        st.session_state.messages.append({"role": "assistant", "content": resposta})
        st.session_state.chat_history.append(AIMessage(content=resposta))

        regex1 = r"\\^!\\[.*\\s\\w*\\]."
        texto = resposta.split('imagens/')[0]
        texto_limpo = re.sub(regex1, "", texto)

        st.chat_message("assistant", avatar="👤").write(texto_limpo)

        try:
            IMG = response['resposta'].split('imagens/')[1].replace('(', '').replace(')','').strip()
            if IMG:
                imagem = f"./imagens/{IMG}".split(".png")[0]
                if imagem:
                    st.markdown(f'<img src="data:image/png;base64,{base64.b64encode(open(f"{imagem}.png", "rb").read()).decode()}" />', unsafe_allow_html=True)
        except:
            pass

    st.session_state.arquivo_processado = False