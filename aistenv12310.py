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
os.chdir(os.path.abspath(os.curdir))

import logging

from dotenv import load_dotenv
load_dotenv()

# Configurar logs
#logging.basicConfig(level=logging.DEBUG)
st.set_page_config(
    layout="wide",
    page_title="AIstein - Assistente Digital",
    page_icon="🤖"
)


def data_legivel():
    data_legivel = datetime.fromtimestamp(datetime.timestamp(datetime.now())).strftime('%Y-%m-%d %H:%M:%S')
    return data_legivel, f"Data e hora do início da conversa: {data_legivel}"

hash_id = ''
def conversaID():
    # DATACAO E HASH ID PARA SESSION E HISTORICO DE CONVERSAS
    datalegivel, _ = data_legivel()
    hash_id = hashlib.sha256(datalegivel.encode('utf-8')).hexdigest()  # Gera o hash usando SHA-256
    return hash_id[1]

# URL do backend FastAPI (ajuste para o seu host se necessário)
API_URL = "https://appaistein-dnaxg3amcthxecfs.eastus2-01.azurewebsites.net/aistein/"

from azure.storage.blob import BlobServiceClient
import uuid

def upload_file_to_blob(file_path, blob_name=None):
    try:
        blob_name = blob_name or f"{uuid.uuid4()}{Path(file_path).suffix}"
        container_name = "chatwpp"
        connection_string = os.environ.get("META_CONN_STRING")

        if not connection_string:
            st.error("❌ META_CONN_STRING não encontrada.")
            return None

        # Use o SAS token como credential, e não o from_connection_string()
        storage_account_url = "https://bluhmstorage.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=connection_string)
        blob_client = blob_service_client.get_container_client(container_name).get_blob_client(blob_name)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        print(f"✅ Upload feito para o Blob: {blob_name}")
        return blob_name

    except Exception as e:
        st.error(f"❌ Erro ao subir para o Blob: {e}")
        print(f"❌ Erro ao subir para o Blob: {e}")
        return None

# Função para serializar o histórico de chat
def serializar_chat_history(chat_history):
    serializado = []
    for message in chat_history:
        if isinstance(message, HumanMessage):
            serializado.append({"role": "user", "content": message.content})
        elif isinstance(message, AIMessage):
            serializado.append({"role": "assistant", "content": message.content})
    return serializado

# Função para simular o caminho do arquivo (já que não podemos acessar o caminho diretamente)
def get_file_name(uploaded_file):
    return uploaded_file if uploaded_file else "Nenhum arquivo selecionado."

# Função para salvar o arquivo temporariamente
def save_uploaded_file(uploaded_file):
    file_extension = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_file.write(uploaded_file.read())
        return temp_file.name

# Função para enviar o prompt para a API
def enviar_prompt_api(prompt, session_id, chat_history):
    try:
        chat_history_serializado = serializar_chat_history(chat_history)
        print(f"Enviando requisição com prompt: {prompt}")
        headers = {
            'Content-Type': 'application/json',
        }

        response = requests.post(
                API_URL,
                headers=headers,
                json={
                    "prompt": prompt,
                    "session_id": session_id,
                    "chat_history": chat_history_serializado,
                },
                timeout=300,
            )
        #logging.debug(f"Resposta gerada pelo agente >>>>>>>>>>>>>>>>> : {response}")
        print(f"RESPOSTA: {response.content}, {response}")

        print(f"Resposta da API: {response.status_code}, {response.text}")
        if response.status_code == 200:
            return response.json()
        else:
            #ogging.debug(f"Erro na API com status {response.status_code}: {response.text}")
            return {"resposta": "Erro na API", "chat_history": chat_history}
    except requests.Timeout:
        #logging.debug("Erro: A solicitação demorou muito tempo para responder.")
        return {"resposta": "Erro: Tempo limite atingido.", "chat_history": chat_history}
    except requests.ConnectionError:
        #logging.debug("Erro: Problema de conexão.")
        return {"resposta": "Erro: Problema de conexão.", "chat_history": chat_history}
    except Exception as e:
        #logging.debug(f"Erro ao enviar a requisição para a API: {e}")
        return {"resposta": f"Erro inesperado: {e}", "chat_history": chat_history}
##################################################################################
# Streamlit UI

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.image('https://grupoportfolio.com.br/portfolio-formacao/wp-content/uploads/sites/2/2020/09/portfolio-tech-negativo-2.png', use_container_width="auto")
    #if st.button("Limpar Histórico"):
    #    st.session_state.chat_history = []
    #    st.session_state.messages = []
    # Componente de upload de arquivo
    uploaded_file = st.file_uploader("Selecione um arquivo", type=["txt", "pdf", "jpg", "png", "csv"])

    # Exibe o histórico de conversa na barra lateral
    if "chat_history" in st.session_state:
        for message in st.session_state["chat_history"]:
            if isinstance(message, HumanMessage):
                st.write(f"**Usuário:** {message.content}")
            elif isinstance(message, AIMessage):
                st.write(f"**Assistente:** {message.content}")

st.title("🗨️ Assistente Digital - AIstein2")

# Verifique se o 'hash_id' já existe na sessão; se não, crie um
if "hash_id" not in st.session_state:
    st.session_state["hash_id"] = conversaID()  # Gerar um hash_id para a sessão

# Inicializar o histórico de chat no estado da sessão, se não existir
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, meu nome é AIstein, sou um assistente digital e vou te auxiliar."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"], avatar="👤").write(msg["content"])

# Verifica se um arquivo foi carregado e envia para o chat
file_name = None

if uploaded_file:
    # uploaded_file = save_uploaded_file(uploaded_file)
    # file_name = get_file_name(uploaded_file)
    local_path = save_uploaded_file(uploaded_file)
    file_name = upload_file_to_blob(local_path)
    prompt = file_name
    print(f"{file_name}")    
    # Adiciona a mensagem no chat assim que o arquivo é carregado, se ainda não estiver no chat
    if not any(msg['content'] == f"Arquivo carregado: {file_name}" for msg in st.session_state.messages):
        st.session_state.messages.append({"role": "user", "content": f"Arquivo carregado: {file_name}"})
        #st.chat_message("user", avatar="👤").write(f"Arquivo carregado: {file_name}")

# Entrada do usuário
chat_input = st.chat_input(placeholder="Digite aqui o que precisa...")

# Decide o prompt com prioridade para o input manual
prompt = chat_input if chat_input else file_name

# Apenas continua se houver um prompt válido
if prompt:
    print(f"<<<<<<<<<<<<<<<<<<<<<<<<<< {prompt} >>>>>>>>>>>>>>>>>>>>>>>>>\n")
    print(st.session_state["chat_history"])

    # Define a mensagem do usuário com base no tipo de prompt
    if prompt == file_name:
        st.session_state.messages.append({"role": "user", "content": f"Arquivo carregado: {file_name}"})
        st.chat_message("user", avatar="🤓").write(f"Arquivo carregado: {file_name}")
        file_name = None  # ⚠️ limpa o file_name para não reaproveitar
        uploaded_file = None
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user", avatar="🤓").write(prompt)

    # Adiciona ao histórico
    st.session_state.chat_history.append(HumanMessage(content=prompt))

    # Usa o hash_id constante para manter a sessão
    hash_id = st.session_state["hash_id"]
    
    with st.spinner("O assistente está processando sua solicitação..."):
        try:
            # Recuperar o histórico de chat da sessão
            chat_history = st.session_state["chat_history"]
            
            # Envia a próxima interação do usuário para o endpoint
            response = enviar_prompt_api(prompt, hash_id, chat_history)
            #print(response)
            #response['resposta'] = "RESPOTA TESTE AQUI..."
            #print(f"RESPOSTA DO ENVIAR_PROMPT_API: {response}")
            resposta = response.get("resposta", "⚠️ Nenhuma resposta recebida da API.")

            # Garantir que a resposta seja sempre uma string
            if not resposta:
                resposta = "❌ Nenhuma resposta foi retornada."
            elif isinstance(resposta, list):
                resposta = "\n".join(map(str, resposta))
            elif isinstance(resposta, dict):
                resposta = str(resposta)

            # Salva no estado do chat
            st.session_state.messages.append({"role": "assistant", "content": resposta})
            st.session_state.chat_history.append(AIMessage(content=resposta))

            # Limpeza visual se necessário
            regex1 = r"\\^!\[.*\s\w*\]."
            texto = resposta.split('imagens/')[0]  # Se tiver imagem, separa do conteúdo
            texto_limpo = re.sub(regex1, "", texto)

            # Exibir a mensagem do assistente
            st.chat_message("assistant", avatar="👤").write(texto_limpo)


            # VERIFICACAO E PLOTAGEM DE IMAGEM CASO EXISTA
            try:
                IMG = response['resposta'].split('imagens/')[1].replace('(', '').replace(')','').strip()
                if IMG:
                    imagem = f"./imagens/{IMG}"
                    imagem_ = imagem.split(".png")[0]
                    if imagem_:
                        # Exibir o gráfico no Streamlit
                        st.markdown(f'<img src="data:image/png;base64,{base64.b64encode(open(f"{imagem_}.png", "rb").read()).decode()}" />', unsafe_allow_html=True)
            except:
                pass

        except Exception as e:
            print(f"ERRO final prompt: {e}")