# 🔮 Oráculo - Assistente RAG Multimodal

Um assistente virtual inteligente construído com **Python** e **Streamlit**, capaz de interpretar e conversar sobre múltiplos formatos de documentos utilizando a arquitetura RAG (Retrieval-Augmented Generation).

## 🚀 Funcionalidades

- **Suporte Multimodal:** Converse diretamente com Sites (URLs), Vídeos do YouTube, PDFs, planilhas CSV e arquivos TXT.
- **Flexibilidade de LLMs:** Escolha dinâmica entre os modelos da **Groq** (família Llama 3) e **OpenAI** (família GPT-4o).
- **Traga sua própria Chave (BYOK):** O sistema permite que o usuário insira sua própria API Key de forma segura através da interface gráfica, evitando custos indesejados no deploy público.
- **Memória de Conversação:** O bot lembra do contexto da conversa atualizando o histórico em tempo real.

## 🛠️ Tecnologias Utilizadas

- **Interface:** [Streamlit](https://streamlit.io/)
- **Orquestração de LLMs:** [LangChain](https://www.langchain.com/)
- **Modelos Integrados:** `langchain-groq` e `langchain-openai`
- **Processamento de Dados:** `PyPDF`, `BeautifulSoup4`, `youtube-transcript-api` e Pandas (via CSVLoader).

## 💻 Como executar localmente

1. Clone este repositório:
   ```bash
   git clone [https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git](https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git)