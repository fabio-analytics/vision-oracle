import streamlit as st
import time
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from loaders import *

# 1. Configuração inicial da página
st.set_page_config(page_title="Assistente VisionDataPro", page_icon="👨‍💻", layout="centered")

# 2. CSS SUPER PERSONALIZADO (Vidro e Animações)
st.markdown("""
<style>
    /* Esconde elementos nativos do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    
    /* FORÇA O FUNDO A SER 100% TRANSPARENTE */
    body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: transparent !important;
        background-color: transparent !important;
    }
    
    /* Remove o espaço em branco no topo */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* Otimiza a caixa de entrada para vidro */
    .stChatInputContainer {
        padding-bottom: 20px !important;
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

    /* ⚡ ANIMAÇÃO DE ENERGIA NA CAIXA DE TEXTO ⚡ */
    @keyframes pulse-glow {
        0% { box-shadow: 0 0 0px rgba(249, 115, 22, 0.1); border-color: rgba(249, 115, 22, 0.3); }
        50% { box-shadow: 0 0 15px rgba(249, 115, 22, 0.5); border-color: rgba(249, 115, 22, 0.9); }
        100% { box-shadow: 0 0 0px rgba(249, 115, 22, 0.1); border-color: rgba(249, 115, 22, 0.3); }
    }
    
    [data-testid="stChatInput"] {
        background-color: rgba(15, 15, 15, 0.8) !important; /* Fundo levemente escuro */
        border-radius: 18px !important;
        animation: pulse-glow 3s infinite !important; /* Chama a animação de pulso */
    }
    
    /* Pinta o ícone da setinha de enviar com o Laranja VisionDataPró */
    [data-testid="stChatInputSubmitButton"] svg {
        fill: #f97316 !important; 
    }
</style>
""", unsafe_allow_html=True)

MEMORIA = ConversationBufferMemory()

def inicializar_assistente():
    if 'chain' not in st.session_state:
        with st.spinner("Conectando aos servidores VisionDataPro..."):
            api_key = st.secrets["GROQ_API_KEY"] 
            documento = carrega_site('https://www.visiondatapro.com/')
            
            # --- O CÉREBRO DA IA: IDENTIDADE VISION-ORACLE ---
            system_message = '''Você é o Vision-Oracle, a Inteligência Artificial Oficial do portfólio de Fábio Santana de Castro (VisionDataPro).
            Sua missão é ser um excelente anfitrião, agindo de forma educada, profissional, direta e séria.
            
            REGRAS DE CONVERSAÇÃO E TAMANHO DAS RESPOSTAS:
            1. SEU NOME É VISION-ORACLE.
            2. SEJA EXTREMAMENTE CONCISO E DIRETO AO PONTO. Suas respostas devem ser curtas e precisas.
            3. Limite suas respostas a no MÁXIMO 2 parágrafos curtos. 
            4. NÃO USE EMOJIS nas suas respostas. Mantenha um tom profissional e limpo.
            5. O usuário vai te dizer o nome dele no início da conversa. Assim que ele disser, cumprimente-o EXATAMENTE com a seguinte estrutura: "Prazer, [Nome do Usuário]! Eu vou estar te ajudando por aqui, tá bom? Como posso ajudá-lo hoje sobre o trabalho do Fábio?"
            6. Responda SEMPRE em português do Brasil.
            7. BLINDAGEM: Se o visitante fizer perguntas fora do escopo profissional (ex: receitas, política), recuse-se educadamente a responder e diga que seu foco é apenas o trabalho do Fábio na Ciência de Dados.
            8. Se o usuário demonstrar interesse em contratar o Fábio, direcione-o imediatamente para a aba de Contato.

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
            
            st.session_state['mensagens'] = [
                {"role": "ai", "content": "Olá! Bem-vindo ao VisionDataPró!\nMeu nome é Vision-Oracle, a Inteligência. Qual o seu?"}
            ]

def main():
    inicializar_assistente()
    
    chain = st.session_state['chain']
    memoria = st.session_state['memoria']
    
    for msg in st.session_state.get('mensagens', []):
        avatar = "👨‍💻" if msg["role"] == "ai" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
        
    input_usuario = st.chat_input('Digite seu nome ou faça uma pergunta...')
    
    if input_usuario:
        st.chat_message('human', avatar="👤").markdown(input_usuario)
        st.session_state['mensagens'].append({"role": "human", "content": input_usuario})
        
        chat_ai = st.chat_message('ai', avatar="👨‍💻")
        
        with chat_ai:
            with st.spinner("Digitando..."):
                time.sleep(2)
            
            resposta = st.write_stream(chain.stream({
                'input': input_usuario, 
                'chat_history': memoria.buffer_as_messages
            }))
        
        memoria.chat_memory.add_user_message(input_usuario)
        memoria.chat_memory.add_ai_message(resposta)
        st.session_state['memoria'] = memoria
        st.session_state['mensagens'].append({"role": "ai", "content": resposta})

if __name__ == '__main__':
    main()