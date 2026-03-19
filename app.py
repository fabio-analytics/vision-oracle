import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from loaders import *

# 1. Configuração inicial da página (Design e Título)
st.set_page_config(page_title="Assistente VisionDataPro", page_icon="🤖", layout="centered")

# 2. CSS Personalizado para esconder as partes feias do Streamlit e deixar limpo para o seu site
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
    # Verifica se o cérebro já foi carregado para não carregar o site toda hora
    if 'chain' not in st.session_state:
        with st.spinner("Conectando aos servidores VisionDataPro..."):
            
            # Aqui ele puxa a chave secreta do cofre do Streamlit
            api_key = st.secrets["GROQ_API_KEY"] 
            
            # Carrega o seu site automaticamente!
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
            
            # Usando o modelo rápido e gratuito da Groq
            chat = ChatGroq(model='llama3-8b-8192', api_key=api_key)
            chain = template | chat
            
            st.session_state['chain'] = chain
            st.session_state['memoria'] = MEMORIA
            
            # Mensagem de boas-vindas inicial que já aparece na tela
            st.session_state['mensagens'] = [{"role": "ai", "content": "Olá! Sou o assistente de Inteligência Artificial do Fábio. Como posso te ajudar a conhecer melhor o trabalho dele na área de Dados hoje?"}]

def main():
    st.header('🤖 Assistente Virtual', divider='orange')
    
    # Chama a inicialização automática
    inicializar_assistente()
    
    chain = st.session_state['chain']
    memoria = st.session_state['memoria']
    
    # Renderiza o histórico de mensagens na tela
    for msg in st.session_state.get('mensagens', []):
        st.chat_message(msg["role"]).markdown(msg["content"])
        
    # Caixa de texto para o visitante digitar
    input_usuario = st.chat_input('Pergunte sobre as habilidades do Fábio...')
    
    if input_usuario:
        # Mostra a pergunta do usuário
        st.chat_message('human').markdown(input_usuario)
        st.session_state['mensagens'].append({"role": "human", "content": input_usuario})
        
        # Gera e mostra a resposta do Oráculo
        chat_ai = st.chat_message('ai')
        resposta = chat_ai.write_stream(chain.stream({
            'input': input_usuario, 
            'chat_history': memoria.buffer_as_messages
        }))
        
        # Salva na memória
        memoria.chat_memory.add_user_message(input_usuario)
        memoria.chat_memory.add_ai_message(resposta)
        st.session_state['memoria'] = memoria
        st.session_state['mensagens'].append({"role": "ai", "content": resposta})

if __name__ == '__main__':
    main()