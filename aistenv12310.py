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
from azure.storage.blob import BlobServiceClient
import uuid

# Configurações iniciais
st.set_page_config(layout="wide", page_title="AIstein - Assistente Digital", page_icon="🤖")
load_dotenv()
os.chdir(os.path.abspath(os.curdir))

API_URL = "https://appaistein-dnaxg3amcthxecfs.eastus2-01.azurewebsites.net/aistein/"
#API_URL = "http://localhost:8000/aistein/"
# Utilitários
def data_legivel():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def conversaID():
    return hashlib.sha256(data_legivel().encode('utf-8')).hexdigest()[1:]

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
        st.error(f"❌ Erro ao subir para o Blob: {e}")
        return None

def download_blob_to_temp_file(blob_name):
    try:
        container_name = "chatwpp"
        connection_string = os.environ.get("META_CONN_STRING")
        storage_account_url = "https://bluhmstorage.blob.core.windows.net"

        blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=connection_string)
        blob_client = blob_service_client.get_container_client(container_name).get_blob_client(blob_name)

        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(blob_name).suffix) as temp_file:
            temp_file.write(blob_client.download_blob().readall())
            return temp_file.name
    except Exception as e:
        st.error(f"❌ Erro ao baixar do Blob: {e}")
        return None

def save_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as temp_file:
        temp_file.write(uploaded_file.read())
        return temp_file.name

def serializar_chat_history(chat_history):
    return [{"role": "user", "content": m.content} if isinstance(m, HumanMessage)
            else {"role": "assistant", "content": m.content} for m in chat_history]

def enviar_prompt_api(prompt, session_id, chat_history):
    print(f"PROMPT ATUAL: {prompt}")
    try:
        response = requests.post(
            API_URL,
            headers={'Content-Type': 'application/json'},
            json={"prompt": prompt, "session_id": session_id, "chat_history": serializar_chat_history(chat_history)},
            timeout=300,
        )
        return response.json() if response.status_code == 200 else {"resposta": "Erro na API"}
    except Exception as e:
        return {"resposta": f"Erro inesperado: {e}"}

# Interface
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.image('https://grupoportfolio.com.br/portfolio-formacao/wp-content/uploads/sites/2/2020/09/portfolio-tech-negativo-2.png', use_container_width="auto")
    uploaded_file = st.file_uploader("Selecione um arquivo", type=["txt", "pdf", "jpg", "png", "csv", "jpeg"])

# Estados iniciais
if "hash_id" not in st.session_state:
    st.session_state["hash_id"] = conversaID()
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, meu nome é AIstein, sou um assistente digital e vou te auxiliar."}]
if "file_temp_path" not in st.session_state:
    st.session_state["file_temp_path"] = None
if "arquivo_processado" not in st.session_state:
    st.session_state["arquivo_processado"] = False
if "enviar_arquivo_prompt" not in st.session_state:
    st.session_state["enviar_arquivo_prompt"] = False
if "prompt_ja_executado" not in st.session_state:
    st.session_state["prompt_ja_executado"] = False
if "ultimo_arquivo_processado" not in st.session_state:
    st.session_state["ultimo_arquivo_processado"] = None


# Título
st.title("🗨️ Assistente Digital - AIstein2")

# Render histórico
for msg in st.session_state.messages:
    st.chat_message(msg["role"], avatar="👤").write(msg["content"])

# Upload de arquivo
if uploaded_file:
    arquivo_nome = uploaded_file.name

    if (
        not st.session_state.arquivo_processado
        and arquivo_nome != st.session_state.ultimo_arquivo_processado
    ):
        local_path = save_uploaded_file(uploaded_file)
        blob_name = upload_file_to_blob(local_path)  # 👈 Aqui pegamos o nome
        if blob_name:
            st.session_state["blob_name"] = blob_name  # 👈 Salva apenas o nome do blob
            st.session_state.arquivo_processado = True
            st.session_state.enviar_arquivo_prompt = True
            st.session_state.ultimo_arquivo_processado = arquivo_nome
            st.rerun()

# Entrada do usuário
chat_input = st.chat_input("Digite aqui o que precisa...")

prompt = None
is_auto_prompt = False

if chat_input:
    prompt = chat_input
    st.session_state["prompt_ja_executado"] = False
elif (
    st.session_state.get("enviar_arquivo_prompt")
    and not st.session_state.get("prompt_ja_executado")
    and st.session_state.get("blob_name")
):
    prompt = st.session_state["blob_name"]  # 👈 Usa o nome do blob como prompt
    is_auto_prompt = True
    st.session_state["prompt_ja_executado"] = True

if prompt:
    msg_prompt = prompt if not is_auto_prompt else "📎 Arquivo enviado para análise."
    st.chat_message("user", avatar="🤓").write(msg_prompt)
    st.session_state.messages.append({"role": "user", "content": msg_prompt})
    st.session_state.chat_history.append(HumanMessage(content=msg_prompt))

    with st.spinner("O assistente está processando sua solicitação..."):
        response = enviar_prompt_api(prompt, st.session_state["hash_id"], st.session_state.chat_history)
        resposta = response.get("resposta", "⚠️ Nenhuma resposta recebida da API.")

        if not isinstance(resposta, str):
            resposta = str(resposta)

        st.session_state.messages.append({"role": "assistant", "content": resposta})
        st.session_state.chat_history.append(AIMessage(content=resposta))

        texto = resposta.split('imagens/')[0]
        texto_limpo = re.sub(r"\\^!\[.*\s\w*\].", "", texto)
        st.chat_message("assistant", avatar="👤").write(texto_limpo)

    if is_auto_prompt:
        st.session_state["enviar_arquivo_prompt"] = False
        st.session_state["arquivo_processado"] = False
        st.session_state["file_temp_path"] = None
        st.session_state["blob_name"] = None  # 👈 limpa o blob_name
        st.session_state["prompt_ja_executado"] = True

    prompt = None
    is_auto_prompt = False