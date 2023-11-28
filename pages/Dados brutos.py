import pandas as pd
import streamlit as st
import requests
import time

st.set_page_config(layout='wide')

@st.cache_data
def msg_sucesso(msg):
    sucesso = st.success(msg,icon="✅")
    time.sleep(5)
    sucesso.empty()

st.title("DADOS BRUTOS")

url = "https://labdados.com/produtos"
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')


with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas:', list(dados.columns), list(dados.columns))
    
st.sidebar.title('Filtros')

with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Produtos', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0,5000))
    
with st.sidebar.expander('Data da Compra'): 
    data_compra = st.date_input(
        'Selecione a data'
        , (
            dados['Data da Compra'].min()
            , dados['Data da Compra'].max()
        )
    )


query = """
Produto in @produtos and \
    @preco[0] <= Preço <= @preco[1] and \
        @data_compra[0] <= `Data da Compra` <= @data_compra[1]
"""

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)


st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas.')
st.markdown(f'Escreva um nome para o arquivo:')
col1,col2 = st.columns(2)

with col1:
    nome_arquivo = st.text_input('', label_visibility="collapsed",value='dados')
    
with col2:
    st.download_button(
        'Download CSV'
        , data = dados_filtrados.to_csv(index= False, encoding='utf-8')
        , file_name=nome_arquivo+'.csv'
        , mime="text/csv"
        , on_click=msg_sucesso("Dados baixados com sucesso")
    )
