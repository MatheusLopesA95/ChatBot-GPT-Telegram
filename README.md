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
   A variável text_splitter recebe a função *text_splitter.RecursiveCharacterTextSplitter* que definirá como o documento será quebrado de forma recursiva em partes menores, para posteriormente serem comparadas com a pergunta afim de achar o trecho mais semelhante. *chunk_size* define o tamanho dos trechos de texto, *chunk_overlap* define a sobreposição (quantas vezes o mesmo bloco de texto será quebrado mas partindo de diferentes pontos) e *separators* define como estará dividido cada bloco de texto, no exemplo há uma quebra dupla de linha. Ajustar esses parâmetros corretamente é muito importante para melhor acertividade nas perguntas, e redução de alucinações pelo modelo generativo. 

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

Tudo que foi apresentado até aqui está no arquivo ChatBotBasico.py e é o cerne do chatbot. 

## Melhorias e economia 

O que foi passado até aqui é o suficiente pra um chatbot que faz consultas a documentos e responde perguntas, entretanto, é importante ressaltar que cada requisição feita a API da openai é pago, mesmo quando a pergunta não tem resposta. Com isso, foram desenvolvidas algumas soluções para evitar gastos desnecessários e também reduzir o número de requisições feitas a API.
Considerando que todo processamento feito a API é cobrado, e o chatbot no telegram fica disponível para qualquer pessoa utilizar, utilizamos a função filters.IDFilter da biblioteca aiogram para limitar o uso somente a usuários permitidos, para isso basta criar uma lista com o id_user e adicionar a função dentro das funcionalidades do bot.


```
usuarios_permitidos=[1234567]

@dp.message_handler(filters.IDFilter(usuarios_permitidos))
async def gpt(message:types.message):

```

Para que o usuário consiga o seu ID, colocamos uma mensagem com a orientação e outra com a função para pegar o ID
```
# Função para capturar o User ID
@dp.message_handler(filters.Command("get_id"))
async def get_user_id(message: aiogram.types.Message):
    user_id = message.from_user.id
    await message.reply(f"Seu User ID é: {user_id}")

#Orientação para usuário não permitido
#Importante não colocar a função de filtro nessa mensagem
@dp.message_handler()
async def welcome(message:types.Message):
    await message.reply('Usuário não autorizado! \nSe você é fiscal da ANTAQ, digite                   /get_id para gerar seu ID e entre em contato com a Fiscalização para conseguir autorização.')

```

O passo seguinte foi gerar um banco de dados para armazenar as perguntas feitas pelo usuário e as respectivas respostas, com isso, poderemos utilizar a busca por similaridade para reutilizar as respostas já armazenadas para responder perguntas semelhantes, evitando uma nova requisição a API. 

Para esse passo, utilizaremos a bilioteca sentence_transformers (https://www.sbert.net/) para transformar em embeddings a mensagem feita pelo usuário e as perguntas armazenadas no banco de dados, se a similaridade, calculada pela semelhança de cossensos, for maior que o valor crítico, que para esse trabalho foi definido como 0.9 após alguns testes, a resposta dada será a armazenada no banco, caso contrário será feita uma requisição para a API para gerar uma nova resposta, e essa será armazenada no banco junto com sua respectiva pergunta.

@dp.message_handler(filters.IDFilter(usuarios_permitidos))
async def gpt(message:types.message):
    message.from_user.id
```
    Pergunta[0]=message.text
    #Transforma a mensagem do usuário em embedding
    Embedding = model.encode(message.text, convert_to_tensor=True)

    #Recebe a tabela do banco de dados, nesse projeto fizemos uma requisição por API para o banco phpmyadmin
    # Atabela pode ser importada por meio de uma query SQL
    #A tabela do banco de dados é importada como um dataframe pandas para que seja possível algumas manipulações
    df=pd.read_json(urllib.request.urlopen(''))

    #Por meio de uma função lambda criamos uma coluna provisória para armazenar os valores de similaridade
    #A função util.cos_sim faz calcula a similaridade de cossenos
    df['similaridade']=df['pergunta'].apply(lambda x: util.cos_sim(model.encode(x, convert_to_tensor=True), Embedding))
    #Ordena o dataframe de acordo com a similaridade
    df = df.sort_values('similaridade', ascending=False).reset_index().head(10)
   
    #Faz a comparação do valor mais similar com o valor crítico, caso retorne true a resposta armazenada é entregue ao usuário, caso retorne false, o bloco faz uma requisição a API por meio da função query_gpt
    if df['similaridade'][0] >= 0.9:
        await message.reply(df['resposta'].iloc[0])
        #Exclui a coluna similaridade para reduzir a alocação em ram
        df = df.drop(columns='similaridade', axis=1)
    else:
        
        await message.reply('Aguarde um momento, estou buscando uma resposta na documentação da Antaq.')
        query_gpt(message.text)

        #Conexão com o banco de dados
        connection = pymysql.connect(host=, 
                                     port=, 
                                     user=, 
                                     password=, 
                                     database=)
        cursor = connection.cursor()

        #Query SQL registra a nova pergunta e nova resposta
        sql = "INSERT INTO chatbot (pergunta, resposta) VALUES (%s, %s)"
        cursor.execute(sql, (message.text, Mensagem[0]))
        connection.insert_id()

        connection.close()
        await message.reply(Mensagem[0])
        await message.reply('⚠️ Resposta incorreta ou incompleta? Digite /reportar')
```
Por último, adicionamos uma função reportar, no caso de alucinações do GPT-3. Em alguns testes o Chat cometeu alucinações quando não havia a resposta na documentação, ou mesmo havendo a informação, em alguns casos raros, houve alguns pequenos erros. 

```
@dp.message_handler(commands=['reportar'])
async def welcome(message:types.Message):
    user_id = message.from_user.id
    #Conexão com o banco
    connection = pymysql.connect(host=, 
                                 port=, 
                                 user=, 
                                 password=, 
                                 database=)
    cursor = connection.cursor()
    #Query SQL de registro 
    sql = f"SELECT id_chat from chatbot where pergunta = '{Pergunta[0]}'"
    cursor.execute(sql)
    id = cursor.fetchone()[0]
    await message.reply(f'Caso a resposta esteja errada, acesse o link: ')
    connection.close()
```
Para o usuário reportar o erro, fizemos um link que direciona para um google forms contendo a pergunta, o ID da pergunta registrada no banco, a resposta e o id do usuário, nesse formulário o usuário aponta os erros que serão checados posterioemente pela equipe técnica e atualizada no banco de dados.

O código final do chatbot é o arquivo ChatBotFinal.py
Os links de API e informações de conexão do banco de dados foram suprimidos por questões de segurança. 
