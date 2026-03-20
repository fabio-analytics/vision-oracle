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
            
            # --- O NOVO CÉREBRO DA IA (REGRAS DE CONDUTA) ---
            system_message = '''Você é o Assistente Virtual Oficial do portfólio de Fábio Santana de Castro (VisionDataPro).
            Sua missão é ser um excelente anfitrião, agindo de forma educada, profissional e amigável.
            
            REGRAS DE CONVERSAÇÃO:
            1. O usuário vai te dizer o nome dele. Assim que ele disser, cumprimente-o usando o nome dele de forma amigável.
            2. Em seguida, pergunte diretamente como você pode ajudá-lo a conhecer melhor o trabalho do Fábio, suas habilidades em Ciência de Dados (como Python, SQL, Power BI, etc.) ou os projetos detalhados no site.
            3. Responda SEMPRE em português do Brasil de forma clara e objetiva. Use emojis ocasionalmente para manter um tom acolhedor (🚀, 📊, 💻).
            4. BLINDAGEM: Se o visitante fizer perguntas fora do escopo profissional, sobre política, religião, receitas, ou qualquer assunto não relacionado a Ciência de Dados e ao Fábio, recuse-se educadamente a responder e diga que seu foco é apenas falar sobre o portfólio e o trabalho do Fábio.
            5. Valorize a experiência do Fábio (nível intermediário em Ciência de Dados, focado em entregar valor) e, se o usuário demonstrar interesse em contrato ou vagas, direcione-o para a aba de Contato do site.

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
            
            # --- A NOVA MENSAGEM DE BOAS-VINDAS INICIAL ---
            st.session_state['mensagens'] = [
                {"role": "ai", "content": "Olá! Seja muito bem-vindo ao portfólio VisionDataPro! 🚀\n\nSou o assistente de Inteligência Artificial do Fábio. Para começarmos bem, como você se chama?"}
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