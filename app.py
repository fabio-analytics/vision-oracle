import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from loaders import *

# 1. Configuração inicial da página (Design e Título)
st.set_page_config(page_title="Assistente VisionDataPro", page_icon="👨‍💻", layout="centered")

# 2. CSS Personalizado para esconder as partes feias do Streamlit
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stChatInputContainer {padding-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

MEMORIA = ConversationBufferMemory()

def inicializar_assistente():
    if 'chain' not in st.session_state:
        with st.spinner("Conectando aos servidores VisionDataPro..."):
            
            # Aqui ele puxa a chave secreta do cofre do Streamlit
            api_key = st.secrets["GROQ_API_KEY"] 
            
            # Carrega o seu site automaticamente
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
            
            # Modelo atualizado e poderoso
            chat = ChatGroq(model='llama-3.3-70b-versatile', api_key=api_key)
            chain = template | chat
            
            st.session_state['chain'] = chain
            st.session_state['memoria'] = MEMORIA
            
            # Mensagem de boas-vindas inicial
            st.session_state['mensagens'] = [{"role": "ai", "content": "Olá! Sou o assistente de Inteligência Artificial do Fábio. Como posso te ajudar a conhecer melhor o trabalho dele na área de Dados hoje?"}]

def main():
    st.header('Assistente Virtual VisionDataPro', divider='orange')
    
    inicializar_assistente()
    
    chain = st.session_state['chain']
    memoria = st.session_state['memoria']
    
    # Renderiza o histórico de mensagens na tela com avatares humanos
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