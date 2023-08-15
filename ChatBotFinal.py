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

model = SentenceTransformer('all-MiniLM-L6-v2')
bot = Bot(token = '')
dp = Dispatcher(bot)
openai.api_key  = ''

#Carregamento da base de dados, no caso, arquivos TXT contidos na pasta ArquivosTXT/
loader = langchain.document_loaders.DirectoryLoader('ArquivosTXT/', glob="**/*.txt", loader_cls=langchain.document_loaders.TextLoader, loader_kwargs={'autodetect_encoding': True})
documents = loader.load()
text_splitter = langchain.text_splitter.RecursiveCharacterTextSplitter(chunk_size = 2300, chunk_overlap  = 10, length_function = len, separators="\n\n")
texts = text_splitter.split_documents(documents)

usuarios_permitidos=[]

Mensagem =['Mensagem']
Pergunta = ['Pergunta']

def query_gpt(input):
    embeddings = langchain.embeddings.OpenAIEmbeddings(openai_api_key = '')
    doc_search = langchain.vectorstores.Chroma.from_documents(texts, embeddings)
    chain = langchain.VectorDBQA.from_chain_type(llm=langchain.OpenAI(openai_api_key = ''), chain_type = 'stuff', vectorstore = doc_search)
    Mensagem[0] = chain.run(input)

# Definir um manipulador para capturar o User ID
@dp.message_handler(filters.Command("get_id"))
async def get_user_id(message: aiogram.types.Message):
    user_id = message.from_user.id
    await message.reply(f"Seu User ID é: {user_id}")

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



@dp.message_handler(filters.IDFilter(usuarios_permitidos) ,commands=['start'])
async def welcome(message:types.Message):
    await message.reply('Olá, eu sou o Bot da ANTAQ. Pergunte-me algo')
    

@dp.message_handler(filters.IDFilter(usuarios_permitidos))
async def gpt(message:types.message):
    message.from_user.id

    Pergunta[0]=message.text

    Embedding = model.encode(message.text, convert_to_tensor=True)

    df=pd.read_json(urllib.request.urlopen(''))


    #Criação de uma coluna provisória para armazenar os valores de similaridade
    df['similaridade']=df['pergunta'].apply(lambda x: util.cos_sim(model.encode(x, convert_to_tensor=True), Embedding))
    df = df.sort_values('similaridade', ascending=False).reset_index().head(10)
   

    if df['similaridade'][0] >= 0.9:
        await message.reply(df['resposta'].iloc[0])
        df = df.drop(columns='similaridade', axis=1)
    else:
        
        await message.reply('Aguarde um momento, estou buscando uma resposta na documentação da Antaq.')
        query_gpt(message.text)

        #Conexão com o banco
        connection = pymysql.connect(host=, 
                                     port=, 
                                     user=, 
                                     password=, 
                                     database=)
        cursor = connection.cursor()

        #Query SQL de registro 
        sql = "INSERT INTO chatbot (pergunta, resposta) VALUES (%s, %s)"
        cursor.execute(sql, (message.text, Mensagem[0]))
        connection.insert_id()

        connection.close()
        await message.reply(Mensagem[0])
        await message.reply('⚠️ Resposta incorreta ou incompleta? Digite /reportar')


@dp.message_handler()
async def welcome(message:types.Message):
    await message.reply('Usuário não autorizado! \nSe você é fiscal da ANTAQ, digite /get_id para gerar seu ID e entre em contato com a Fiscalização para conseguir autorização.')

if __name__ =='__main__':
    executor.start_polling(dp)


