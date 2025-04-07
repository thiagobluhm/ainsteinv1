# from langchain_core.messages import AIMessage, HumanMessage
# import streamlit as st
# import requests
# import hashlib
# from datetime import datetime

# import os
# os.chdir(os.path.abspath(os.curdir))

# def data_legivel():
#     data_legivel = datetime.fromtimestamp(datetime.timestamp(datetime.now())).strftime('%Y-%m-%d %H:%M:%S')
#     return data_legivel, f"Data e hora do início da conversa: {data_legivel}"

# hash_id = ''
# def conversaID():
#     # DATACAO E HASH ID PARA SESSION E HISTORICO DE CONVERSAS
#     datalegivel, _ = data_legivel()
#     hash_id = hashlib.sha256(datalegivel.encode('utf-8')).hexdigest()  # Gera o hash usando SHA-256
#     return hash_id[1]

# # URL do backend FastAPI (ajuste para o seu host se necessário)
# API_URL = "https://appaistein-dnaxg3amcthxecfs.eastus2-01.azurewebsites.net/aistein/"

# # Função para serializar o histórico de chat
# def serializar_chat_history(chat_history):
#     serializado = []
#     for message in chat_history:
#         if isinstance(message, HumanMessage):
#             serializado.append({"role": "user", "content": message.content})
#         elif isinstance(message, AIMessage):
#             serializado.append({"role": "assistant", "content": message.content})
#     return serializado

# # Função para simular o caminho do arquivo (já que não podemos acessar o caminho diretamente)
# def get_file_name(uploaded_file):
#     return uploaded_file.name if uploaded_file else "Nenhum arquivo selecionado."

# # Função para enviar o prompt para a API
# def enviar_prompt_api(prompt, session_id, chat_history):
#     try:
#         # Enviar uma requisição POST para a API FastAPI
#         chat_history_serializado = serializar_chat_history(chat_history)
#         response = requests.post(API_URL, json={
#             "prompt": prompt,
#             "session_id": session_id,
#             "chat_history": chat_history_serializado
#         })
        
#         # Verificar se a requisição foi bem-sucedida
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return {"resposta": "Erro na API", "chat_history": chat_history}
    
#     except requests.Timeout:
#         print("Erro: A solicitação demorou muito tempo para responder.")
#     except requests.ConnectionError:
#         print("Erro: Problema de conexão.")
#     except Exception as e:
#         print(f"Erro ao enviar a requisição para a API: {e}")

# ##################################################################################
# # Streamlit UI

# with open("style.css") as f:
#     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# with st.sidebar:
#     st.image('https://sindojus-ce.org.br/wp-content/uploads/2016/10/unifor-logo-358x358.jpg', use_container_width="auto")
#     #if st.button("Limpar Histórico"):
#     #    st.session_state.chat_history = []
#     #    st.session_state.messages = []
#     # Componente de upload de arquivo
#     uploaded_file = st.file_uploader("Selecione um arquivo", type=["txt", "pdf", "jpg", "png", "csv"])

#     # Exibe o histórico de conversa na barra lateral
#     if "chat_history" in st.session_state:
#         for message in st.session_state["chat_history"]:
#             if isinstance(message, HumanMessage):
#                 st.write(f"**Usuário:** {message.content}")
#             elif isinstance(message, AIMessage):
#                 st.write(f"**Assistente:** {message.content}")

# st.title("🗨️ Assistente Digital - AIsten")

# # Verifique se o 'hash_id' já existe na sessão; se não, crie um
# if "hash_id" not in st.session_state:
#     st.session_state["hash_id"] = conversaID()  # Gerar um hash_id para a sessão

# # Inicializar o histórico de chat no estado da sessão, se não existir
# if "chat_history" not in st.session_state:
#     st.session_state["chat_history"] = []

# if "messages" not in st.session_state:
#     st.session_state["messages"] = [{"role": "assistant", "content": "Olá, eu sou o assistente digital e vou te auxiliar."}]

# for msg in st.session_state.messages:
#     st.chat_message(msg["role"], avatar="👤").write(msg["content"])


# # Verifica se um arquivo foi carregado e envia para o chat
# file_name = None
# if uploaded_file:
#     file_name = get_file_name(uploaded_file)
#     print(f"AQUIIIIIIIIIIII {file_name}")
#     # Adiciona a mensagem no chat assim que o arquivo é carregado, se ainda não estiver no chat
#     if not any(msg['content'] == f"Arquivo carregado: {file_name}" for msg in st.session_state.messages):
#         st.session_state.messages.append({"role": "user", "content": f"Arquivo carregado: {file_name}"})
#         #st.chat_message("user", avatar="👤").write(f"Arquivo carregado: {file_name}")

# # Entrada do usuário
# if prompt := st.chat_input(placeholder="Digite aqui o que precisa...") or file_name:
#     print(f"<<<<<<<<<<<<<<<<<<<<<<<<<< {prompt} >>>>>>>>>>>>>>>>>>>>>>>>>\n")
#     print(st.session_state["chat_history"])
#     if prompt == file_name:
#         # Adiciona a mensagem com o nome do arquivo que foi escolhido
#         st.session_state.messages.append({"role": "user", "content": f"Arquivo carregado: {file_name}"})
#         uploaded_file = None
#     else:
#         # Adiciona a mensagem do usuário ao chat
#         st.session_state.messages.append({"role": "user", "content": prompt})
        
#     st.session_state.chat_history.append(HumanMessage(content=prompt))  # Adiciona a mensagem do usuário ao chat_history
#     st.chat_message("user", avatar="🤓").write(prompt)

#     # Usa o hash_id constante para manter a sessão
#     hash_id = st.session_state["hash_id"]

#     with st.spinner("O assistente está processando sua solicitação..."):
#         try:
#             # Recuperar o histórico de chat da sessão
#             chat_history = st.session_state["chat_history"]
            
#             # Envia a próxima interação do usuário para o endpoint
#             response = enviar_prompt_api(prompt, hash_id, chat_history)
#             st.session_state.messages.append({"role": "assistant", "content": response["resposta"]})
#             st.session_state.chat_history.append(AIMessage(content=response["resposta"]))  # Adiciona a resposta ao chat_history
#             st.chat_message("assistant", avatar="🤓").write(response["resposta"])

#         except Exception as e:
#             print(f"ERRO final prompt: {e}")


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

# Configurar logs
#logging.basicConfig(level=logging.DEBUG)

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
    st.image('https://sindojus-ce.org.br/wp-content/uploads/2016/10/unifor-logo-358x358.jpg', use_container_width="auto")
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

st.title("🗨️ Assistente Digital - AIstein")

# Verifique se o 'hash_id' já existe na sessão; se não, crie um
if "hash_id" not in st.session_state:
    st.session_state["hash_id"] = conversaID()  # Gerar um hash_id para a sessão

# Inicializar o histórico de chat no estado da sessão, se não existir
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, meu nome é AIstein sou um assistente digital e vou te auxiliar."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"], avatar="👤").write(msg["content"])

# Verifica se um arquivo foi carregado e envia para o chat
file_name = None

if uploaded_file:
    uploaded_file = save_uploaded_file(uploaded_file)
    file_name = get_file_name(uploaded_file)
    print(f"{file_name}")
    # Adiciona a mensagem no chat assim que o arquivo é carregado, se ainda não estiver no chat
    if not any(msg['content'] == f"Arquivo carregado: {file_name}" for msg in st.session_state.messages):
        st.session_state.messages.append({"role": "user", "content": f"Arquivo carregado: {file_name}"})
        #st.chat_message("user", avatar="👤").write(f"Arquivo carregado: {file_name}")

# Entrada do usuário
if prompt := st.chat_input(placeholder="Digite aqui o que precisa...") or file_name:
    print(f"<<<<<<<<<<<<<<<<<<<<<<<<<< {prompt} >>>>>>>>>>>>>>>>>>>>>>>>>\n")
    print(st.session_state["chat_history"])
    if prompt == file_name:
        # Adiciona a mensagem com o nome do arquivo que foi escolhido
        st.session_state.messages.append({"role": "user", "content": f"Arquivo carregado: {file_name}"})
        uploaded_file = None
    else:
        # Adiciona a mensagem do usuário ao chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
    st.session_state.chat_history.append(HumanMessage(content=prompt))  # Adiciona a mensagem do usuário ao chat_history
    st.chat_message("user", avatar="🤓").write(prompt)

    # Usa o hash_id constante para manter a sessão
    hash_id = st.session_state["hash_id"]
    
    with st.spinner("O assistente está processando sua solicitação..."):
        try:
            # Recuperar o histórico de chat da sessão
            chat_history = st.session_state["chat_history"]
            
            # Envia a próxima interação do usuário para o endpoint
            response = enviar_prompt_api(prompt, hash_id, chat_history)
            print(response)
            #response['resposta'] = "RESPOTA TESTE AQUI..."
            print(f"RESPOSTA DA ENVIAR_PROMPT_API: {response}")

            st.session_state.messages.append({"role": "assistant", "content": response["resposta"]})
            st.session_state.chat_history.append(AIMessage(content=response["resposta"]))  # Adiciona a resposta ao chat_history
            regex1 = r"\\^!\[.*\s\w*\]."
            texto = response['resposta'].split('imagens/')[0]
            texto_limpo = re.sub(regex1, "", texto)
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
