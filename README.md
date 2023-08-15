## Como fazer um chatbot básico com GPT3.0 para o serviço público.
  Segundo a Oracle  “Um chatbot é um programa de computador que simula e processa conversas humanas (escritas ou faladas), permitindo que as pessoas interajam com dispositivos digitais como se estivessem se comunicando com uma pessoa real.”. Atualmente a maioria dos ChatBots estão sendo utilizados para atendimentos de call center, mas limitados a um arsenal de poucas respostas prontas feitas pelo programador. 

 Com o lançamento de inteligências artificiais generativas, como o GPT-3 da Openai, a possibilidade de respostas de ChatBots não fica limitado apenas ao que um programador conseguiu colocar em estruturas de if else. Com essa ferramenta, as respostas agora podem ser feitas a partir da consulta de documentos e são geradas instantaneamente de acordo com a pergunta feita. 
 
No setor público o uso de ChatBots pode ser utilizado tanto para o atendimento ao usuário de alguns serviços, para esclarecer dúvidas, agendar serviços ou para o uso interno, como solucionar duvidas dos servidores e realizar consulta a documentos. O presente projeto tem como objetivo automatizar consulta a documentos, a fim de melhorar o desempenho e qualidade do trabalho dos fiscais da ANTAQ.

A seguir vamos ensinar como programar um chatbot do telegram que busca respostas em documentações específicas usando a linguagem Python. 

Vamos ao código:
 
 Começando com a importação das bibliotecas
```
import langchain 
import openai
import pymysql
import pandas as pd
import aiogram
import urllib
from sentence_transformers import SentenceTransformer, util
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import filters
from openai.embeddings_utils import get_embedding, cosine_similarity
```
O primeiro passo é conseguir uma key do telegram e da openai. É possível conseguir uma key do telegram buscando o BotFather na sua lista de contatos. Para conseguir a key da openai bastar ir na API e procurar por View API Key no canto superior direito da tela. Com a key do Telegram, você poderá associar o bot ao código e também criar uma lista para armazenar strings.
```
bot = Bot(token = 'SEU_TOKEN')
dp = Dispatcher(bot)

Mensagem =['Mensagem']
```

  A conexão entre o GPT-3 e a documentação a qual será utilizada para gerar as respostas é feito por meio da biblioteca LangChain (https://python.langchain.com/).
 
 
 
   A variável loader recebe os documentos por meio da função document_loaders.DirectoryLoader, a qual recebe como parâmetros a pasta onde estão inseridos os documentos, o formato(glob=), e o tipo de estrutura (loader_cls=).  
```
loader = langchain.document_loaders.DirectoryLoader('Directory/', 
                                                    glob="**/*.txt", 
                                                    loader_cls=langchain.document_loaders.TextLoader)
documents = loader.load()
len(documents)
text_splitter = langchain.text_splitter.RecursiveCharacterTextSplitter(chunk_size =2300, 
                                                                       chunk_overlap  =10, 
                                                                       length_function =len, 
                                                                       separators="\n\n")
texts = text_splitter.split_documents(documents)
```
   A variável text_splitter recebe a função *text_splitter.RecursiveCharacterTextSplitter* que definirá como o documento será quebrado de forma recursiva em partes menores, para posteriormente serem comparadas com a pergunta afim de achar o trecho mais semelhante. *chunk_size* define o tamanho dos trechos de texto, *chunk_overlap* define a sobreposição (quantas vezes o mesmo bloco de texto será quebrado mas partindo de diferentes pontos) e *separators* define como estará dividido cada bloco de texto, no exemplo há uma quebra dupla de linha.

```
def query_gpt(input):
    embeddings = langchain.embeddings.OpenAIEmbeddings(openai_api_key = 'MY_OPENAI_KEY')
    doc_search = langchain.vectorstores.Chroma.from_documents(texts, embeddings)
    chain = langchain.VectorDBQA.from_chain_type(llm=langchain.OpenAI(openai_api_key = 'MY_OPENAI_KEY'), 
                                                 chain_type = 'stuff', 
                                                 vectorstore = doc_search)
    Mensagem[0] = chain.run(input)
```

 A função *query_gpt()* receberá uma sentença feita pelo usuário, transformará essa sentença um vetor contendo embeddings (representações numéricas de cada palavra), transformará cada trecho dividido em *text_splitter*, posteriormente fará as comparações e retornará um texto. Esse texto será atribuído a posição 0 de uma lista para que possa ser usado posteriormente como resposta para o chatbot do telegram. Caso não exista trecho com semelhança suficiente, o modelo responderá que não sabe, entretanto em algumas raras ocasiões pode ocorrer a escrita de textos delirantes.  
	
 Para que o usuário possa interagir com o gpt por meio do telegram, deve-se colocar a mensagem como parâmetro da função query_gpt para que a função possa processar a pergunta, pesquisar nos documentos e gerar a resposta. Para que o telegram responda o usuário, deve-se colocar a posição 0 da lista *Mensagem* na função de resposta. 

```
@dp.message_handler()
async def gpt(message:types.message):
    query_gpt(message.text)
    await message.reply(Mensagem[0])
``` 

