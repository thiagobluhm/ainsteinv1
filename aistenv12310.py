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

def save_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as temp_file:
        temp_file.write(uploaded_file.read())
        return temp_file.name

def serializar_chat_history(chat_history):
    return [{"role": "user", "content": m.content} if isinstance(m, HumanMessage)
            else {"role": "assistant", "content": m.content} for m in chat_history]

def enviar_prompt_api(prompt, session_id, chat_history):
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
if "file_name_from_blob" not in st.session_state:
    st.session_state["file_name_from_blob"] = None
if "arquivo_processado" not in st.session_state:
    st.session_state["arquivo_processado"] = False

# Título
st.title("🗨️ Assistente Digital - AIstein2")

# Render histórico
for msg in st.session_state.messages:
    st.chat_message(msg["role"], avatar="👤").write(msg["content"])

# Upload de arquivo
if uploaded_file and not st.session_state.arquivo_processado:
    local_path = save_uploaded_file(uploaded_file)
    blob_name = upload_file_to_blob(local_path)
    st.session_state["file_name_from_blob"] = blob_name
    st.session_state.arquivo_processado = True
    st.rerun()

# Entrada do usuário
chat_input = st.chat_input("Digite aqui o que precisa...")
prompt = chat_input if chat_input else (
    f"Arquivo carregado: {st.session_state['file_name_from_blob']}"
    if st.session_state["file_name_from_blob"] else None
)

# Processa prompt
if prompt:
    # Exibe e salva a mensagem do usuário
    st.chat_message("user", avatar="🤓").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.chat_history.append(HumanMessage(content=prompt))

    with st.spinner("O assistente está processando sua solicitação..."):
        response = enviar_prompt_api(prompt, st.session_state["hash_id"], st.session_state.chat_history)
        resposta = response.get("resposta", "⚠️ Nenhuma resposta recebida da API.")

        if not isinstance(resposta, str):
            resposta = str(resposta)

        st.session_state.messages.append({"role": "assistant", "content": resposta})
        st.session_state.chat_history.append(AIMessage(content=resposta))

        # Limpa eventual lixo visual
        texto = resposta.split('imagens/')[0]
        texto_limpo = re.sub(r"\\^!\[.*\s\w*\].", "", texto)
        st.chat_message("assistant", avatar="👤").write(texto_limpo)

        # Exibe imagem de resposta, se houver
        try:
            IMG = response['resposta'].split('imagens/')[1].replace('(', '').replace(')', '').strip()
            imagem = f"./imagens/{IMG}".split(".png")[0]
            if imagem:
                st.markdown(f'<img src="data:image/png;base64,{base64.b64encode(open(f"{imagem}.png", "rb").read()).decode()}" />', unsafe_allow_html=True)
        except:
            pass

    # Limpa variáveis de controle
    st.session_state["arquivo_processado"] = False
    st.session_state["file_name_from_blob"] = None
