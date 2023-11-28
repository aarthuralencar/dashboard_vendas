import pandas as pd
import streamlit as st
import requests
import plotly.express as px

st.set_page_config(layout='wide')

def formata_numero(valor,prefixo = ""): 
    for unidade in ['','mil']:
        if valor < 1000:
            return f"{prefixo} {valor:.2f} {unidade}"
        valor /=1000
        
    return f"{prefixo} {valor:.2f} MM"


st.title("DASHBOARD DE VENDAS :shopping_trolley:")

url = "https://labdados.com/produtos"

regioes = [
    'Brasil'
    ,'Centro-oeste'
    ,'Nordeste'
    ,'Norte'
    ,'Sudeste'
    ,'Sul'
]

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região',regioes)

if regiao =='Brasil':
    regiao = ''
    
todos_anos = st.sidebar.checkbox('Dados de todo o período',value=True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano',2020,2023)

query_string = {'regiao':regiao.lower(),'ano':ano}
response = requests.get(url,params=query_string)

dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores',dados['Vendedor'].unique())

if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################
##Tabelas de receita 
##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################


receita_estados = dados\
    .groupby(['Local da compra','lat','lon'])['Preço'].sum()\
        .reset_index()\
            .sort_values('Preço',ascending=False)
            
            
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço']\
    .sum()\
        .reset_index()            
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()


receita_categorias = dados\
    .groupby(['Categoria do Produto'])['Preço'].sum()\
        .reset_index()\
            .sort_values('Preço',ascending=False)

##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################
##Tabelas de Qtde 
##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################


#Tabelas de quantidade
qtde_estados = dados\
    .groupby(['Local da compra','lat','lon'])['Produto'].count()\
        .reset_index()\
            .sort_values('Produto',ascending=False)
            
            
qtde_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Produto']\
    .count()\
        .reset_index()            
qtde_mensal['Ano'] = qtde_mensal['Data da Compra'].dt.year
qtde_mensal['Mês'] = qtde_mensal['Data da Compra'].dt.month_name()


qtde_categorias = dados\
    .groupby(['Categoria do Produto'])['Produto'].count()\
        .reset_index()\
            .sort_values('Produto',ascending=False)


##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################
## Vendedor
##############################################################################################
##############################################################################################
##############################################################################################
##############################################################################################
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(
    'sum'
    ,'avg'
))

##Gráficos 
fig_mapa_receita = px.scatter_geo(
    receita_estados
    ,lat='lat'
    ,lon='lon'
    ,scope='south america'
    ,size='Preço'
    ,template='seaborn'
    ,hover_name='Local da compra'
    ,hover_data={
        'lat':False,'lon':False
    }
    ,title="Receita por estado"
    )

fig_receita_mensal = px.line(
    receita_mensal
    ,x = 'Mês'
    ,y = 'Preço'
    ,markers=True
    ,range_y = (0,receita_mensal.max())
    ,color='Ano'
    ,line_dash='Ano'
    ,title='Receita mensal'
)

fig_receita_mensal.update_layout(yaxis_title='Receita')

fig_receita_estados = px.bar(
    receita_estados.head(10)
    ,x='Local da compra'
    ,y='Preço'
    ,text_auto=True
    ,title="Top estados (Receita)"
)

fig_receita_estados.update_layout(
    yaxis_title = "Receita"
)

fig_receita_categorias = px.bar(
    receita_categorias
    ,x='Categoria do Produto'
    ,y='Preço'
    ,text_auto=True
    ,title="Receita por categoria"
)

fig_receita_categorias.update_layout(
    yaxis_title = "Receita"
)


fig_mapa_qtde = px.scatter_geo(
    qtde_estados
    ,lat='lat'
    ,lon='lon'
    ,scope='south america'
    ,size='Produto'
    ,template='seaborn'
    ,hover_name='Local da compra'
    ,hover_data={
        'lat':False,'lon':False
    }
    ,title="Quantidade por estado"
    )

fig_qtde_mensal = px.line(
    qtde_mensal
    ,x = 'Mês'
    ,y = 'Produto'
    ,markers=True
    ,range_y = (0,qtde_mensal.max())
    ,color='Ano'
    ,line_dash='Ano'
    ,title='Quantidade mensal'
)

fig_qtde_mensal.update_layout(yaxis_title='Quantidade')

fig_qtde_estados = px.bar(
    qtde_estados.head(10)
    ,x='Local da compra'
    ,y='Produto'
    ,text_auto=True
    ,title="Top estados (Qtd)"
)

fig_qtde_estados.update_layout(
    yaxis_title = "Quantidade (#)"
)

fig_qtde_categorias = px.bar(
    qtde_categorias
    ,x='Categoria do Produto'
    ,y='Produto'
    ,text_auto=True
    ,title="Quantidade por categoria"
)

fig_qtde_categorias.update_layout(
    yaxis_title = "Quantidade (#)"
)



#Abas
aba1,aba2,aba3 = st.tabs([
    'Receita'
    ,'Quantidade'
    ,'Vendedores'
])


#Páginas  
with aba1:
    #Colunas 
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric("Receita total", formata_numero(dados['Preço'].sum(),"R$"))
        st.plotly_chart(fig_mapa_receita,use_container_width=True)
        st.plotly_chart(fig_receita_estados,use_container_width=True)
    with coluna2:
        st.metric("Quantidade de vendas", formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal,use_container_width=True)
        st.plotly_chart(fig_receita_categorias,use_container_width=True)
        
with aba2:
    #Colunas 
    coluna1,coluna2 = st.columns(2)

    with coluna1:
        st.metric("Receita total", formata_numero(dados['Preço'].sum(),"R$"))
        st.plotly_chart(fig_mapa_qtde,use_container_width=True)
        st.plotly_chart(fig_qtde_estados,use_container_width=True)
    with coluna2:
        st.metric("Quantidade de vendas", formata_numero(dados.shape[0]))
        st.plotly_chart(fig_qtde_mensal,use_container_width=True)
        st.plotly_chart(fig_qtde_categorias,use_container_width=True)
with aba3:
    qtd_vendedores = st.number_input("Quantidade de vendedores",2,10,5)
    #Colunas 
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric("Receita total", formata_numero(dados['Preço'].sum(),"R$"))
    with coluna2:
        st.metric("Quantidade de vendas", formata_numero(dados.shape[0]))

st.dataframe(dados)
# st.dataframe(receita_estados)
