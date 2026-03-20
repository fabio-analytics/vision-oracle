import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from loaders import *

# 1. Configuração inicial da página
st.set_page_config(page_title="Assistente VisionDataPro", page_icon="👨‍💻", layout="centered")

# 2. CSS SUPER PERSONALIZADO (Transparência total e Efeito Vidro)
st.markdown("""
<style>
    /* Esconde elementos nativos do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 🔴 FORÇA O FUNDO A SER 100% TRANSPARENTE 🔴 */
    body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: transparent !important;
        background-color: transparent !important;
    }
    
    /* Remove o espaço em branco no topo */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    /* Otimiza a caixa de entrada para vidro */
    .stChatInputContainer {
        padding-bottom: 20px;
        background: transparent !important;
    }

    /* 🔮 EFEITO VIDRO NAS MENSAGENS DO CHAT */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 15px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    }

    /* 🔮 EFEITO VIDRO NOS AVATARES */
    [data-testid="stChatMessageAvatar"] {
        background-color: rgba(249, 115, 22, 0.15) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(249, 115, 22, 0.4) !important;
        border-radius: 50% !important;
    }
</style>
""", unsafe_allow_html=True)

MEMORIA = ConversationBufferMemory()

def inicializar_assistente():
    if 'chain' not in st.session_state:
        with st.spinner("Conectando aos servidores VisionDataPro..."):
            api_key = st.secrets["GROQ_API_KEY"] 
            documento = carrega_site('https://www.visiondatapro.com/')
            
            system_message = '''Você é o Assistente Virtual Oficial do portfólio de Fábio Santana de Castro (VisionDataPro).
            O seu objetivo é ser cordial, profissional e ajudar os visitantes a entenderem as habilidades, projetos e a experiência do Fábio.
            Responda SEMPRE em português do Brasil de forma clara e objetiva. Valorize o trabalho do Fábio como Cientista de Dados.
            Use estas informações do site dele para basear suas respostas:
            ####
            {}
            ####
            '''.format(documento)
            
            template = ChatPromptTemplate.from_messages([
                ('system', system_message),
                ('placeholder', '{chat_history}'),
                ('user', '{input}')
            ])
            
            chat = ChatGroq(model='llama-3.3-70b-versatile', api_key=api_key)
            chain = template | chat
            
            st.session_state['chain'] = chain
            st.session_state['memoria'] = MEMORIA
            st.session_state['mensagens'] = [{"role": "ai", "content": "Olá! Sou o assistente de Inteligência Artificial do Fábio. Como posso te ajudar a conhecer melhor o trabalho dele na área de Dados hoje?"}]

def main():
    inicializar_assistente()
    
    chain = st.session_state['chain']
    memoria = st.session_state['memoria']
    
    for msg in st.session_state.get('mensagens', []):
        avatar = "👨‍💻" if msg["role"] == "ai" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
        
    input_usuario = st.chat_input('Pergunte sobre as habilidades do Fábio...')
    
    if input_usuario:
        st.chat_message('human', avatar="👤").markdown(input_usuario)
        st.session_state['mensagens'].append({"role": "human", "content": input_usuario})
        
        chat_ai = st.chat_message('ai', avatar="👨‍💻")
        resposta = chat_ai.write_stream(chain.stream({
            'input': input_usuario, 
            'chat_history': memoria.buffer_as_messages
        }))
        
        memoria.chat_memory.add_user_message(input_usuario)
        memoria.chat_memory.add_ai_message(resposta)
        st.session_state['memoria'] = memoria
        st.session_state['mensagens'].append({"role": "ai", "content": resposta})

if __name__ == '__main__':
    main()