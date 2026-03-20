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
</style>
""", unsafe_allow_html=True)

MEMORIA = ConversationBufferMemory()

def inicializar_assistente():
    if 'chain' not in st.session_state:
        with st.spinner("Conectando aos servidores VisionDataPro..."):
            api_key = st.secrets["GROQ_API_KEY"] 
            documento = carrega_site('https://www.visiondatapro.com/')
            
            # --- O CÉREBRO DA IA: AGORA COM REGRAS DE RESPOSTA CURTA ---
            system_message = '''Você é o Assistente Virtual Oficial do portfólio de Fábio Santana de Castro (VisionDataPro).
            Sua missão é ser um excelente anfitrião, agindo de forma educada, profissional e amigável.
            
            REGRAS DE CONVERSAÇÃO E TAMANHO DAS RESPOSTAS:
            1. SEJA EXTREMAMENTE CONCISO E DIRETO AO PONTO. Suas respostas devem ser curtas, precisas e fáceis de ler. NUNCA escreva textos longos.
            2. Limite suas respostas a no MÁXIMO 2 ou 3 parágrafos curtos. 
            3. Se for listar habilidades ou projetos, cite apenas os 2 ou 3 mais importantes e convide o usuário a explorar o site para ver o resto.
            4. O usuário vai te dizer o nome dele no início. Assim que ele disser, cumprimente-o pelo nome de forma amigável e pergunte rapidamente como pode ajudar.
            5. Responda SEMPRE em português do Brasil. Use emojis ocasionalmente para manter um tom moderno (🚀, 📊, 💻).
            6. BLINDAGEM: Se o visitante fizer perguntas fora do escopo profissional (ex: receitas, política), recuse-se educadamente a responder e diga que seu foco é apenas o trabalho do Fábio na Ciência de Dados.
            7. Se o usuário demonstrar interesse em contratar o Fábio, direcione-o imediatamente para a aba de Contato.

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
            
            # Mensagem inicial curta e direta
            st.session_state['mensagens'] = [
                {"role": "ai", "content": "Olá! Bem-vindo ao VisionDataPro! 🚀\n\nSou a Inteligência Artificial do Fábio. Para começarmos bem, qual é o seu nome?"}
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