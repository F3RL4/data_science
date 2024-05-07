######################################################################################
# Nome: Edimar Ferla de Almeida                                                      #
# RGM: 29123780                                                                      #
# Instituição: UNIFRAN - Universidade de Franca - Polo Valinhos                      #
# Curso: Bacharelado em Ciências da Computação                                       #
# Disciplina: Visualização de Dados                                                  #
# Link do dataset utilizado: https://www.kaggle.com/datasets/gregorut/videogamesales #
######################################################################################

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

# Carregar e pré-processar os dados
df = pd.read_csv('vgsales.csv')

# Limpeza e filragem dos dados relevantes
df.dropna(inplace=True)
df = df[(df['Year'] > 1980) & (df['Year'] < 2020)] 

# Mapeamento de regiões por países
region_mapping = {
    'NA_Sales': ['United States', 'Canada', 'Mexico'],
    'EU_Sales': ['United Kingdom', 'Germany', 'France', 'Italy', 'Spain', 'Russia'],
    'JP_Sales': ['Japan'],
    'Other_Sales': ['Brazil', 'Australia', 'China', 'India', 'South Korea', 'South Africa']
}

# Função para agregar as vendas por país
def aggregate_sales_by_country(df, region_mapping):
    sales_data = []
    for region, countries in region_mapping.items():
        for country in countries:
            region_sales = df[region].sum()
            sales_data.append({'Country': country, 'Sales': region_sales})
    return pd.DataFrame(sales_data)

# Agregar vendas por país
df_country_sales = aggregate_sales_by_country(df, region_mapping)

# Vendas Globais por Plataforma com Agrupamento "Menor 1%"
platform_sales = df.groupby('Platform').sum().reset_index()
total_global_sales = platform_sales['Global_Sales'].sum()
platform_sales['Percentage'] = (platform_sales['Global_Sales'] / total_global_sales) * 100

# Separar as plataformas com menos de 1% das vendas
platform_less_than_1 = platform_sales[platform_sales['Percentage'] < 1].copy()
other_sales = platform_less_than_1['Global_Sales'].sum()
platform_sales = platform_sales[platform_sales['Percentage'] >= 1]

# Adicionar a categoria "Menor 1%"
other_sales_data = pd.DataFrame([{'Platform': 'Menor 1%', 'Global_Sales': other_sales, 'Percentage': (other_sales / total_global_sales) * 100}])
platform_sales = pd.concat([platform_sales, other_sales_data], ignore_index=True)

# Vendas Anuais por Plataforma - Gráfico de Linha
platform_year_sales = df.groupby(['Year', 'Platform']).sum().reset_index()

# Inicializar o App Dash
app = Dash(__name__)
app.layout = html.Div([
    html.H1('Análise de Vendas de Video Games'),

    # Vendas Globais por Plataforma - Gráfico de Rosca com Campo "Menor 1%"
    html.H2('Comparativo de Vendas por Plataforma'),
    dcc.Graph(
        figure=px.pie(platform_sales, names='Platform', values='Global_Sales',
                      title='Comparativo de Vendas Globais por Plataforma', labels={'Global_Sales': 'Vendas Globais (em milhões)'},
                      hole=0.4).update_traces(textposition='inside', textinfo='percent+label')
    ),

    # Vendas Anuais Globais - Gráfico de Linhas
    html.H2('Vendas Anuais Globais'),
    dcc.Graph(
        figure=px.line(df.groupby('Year').sum().reset_index(), x='Year', y='Global_Sales',
                       title='Vendas Anuais Globais', labels={'Global_Sales': 'Vendas Globais (em milhões)'})
    ),

    # Comparativo de Vendas Anuais por Plataforma - Gráfico de Linha
    html.H2('Comparativo de Vendas Anuais por Plataforma'),
    dcc.Graph(
        figure=px.line(platform_year_sales, x='Year', y='Global_Sales', color='Platform',
                       title='Comparativo de Vendas Anuais por Plataforma', labels={'Global_Sales': 'Vendas Globais (em milhões)'})
    ),

    # Top 10 Jogos mais Vendidos - Gráfico de Barras
    html.H2('Top 10 Jogos mais Vendidos'),
    dcc.Graph(
        figure=px.bar(df.nlargest(10, 'Global_Sales'), x='Name', y='Global_Sales', color='Platform',
                      title='Top 10 Jogos mais Vendidos Globalmente', labels={'Global_Sales': 'Vendas Globais (em milhões)'})
    ),

    # Vendas por País - Mapa Mundí
    html.H2('Distribuição de Vendas de Video Games por País'),
    dcc.Graph(
        figure=px.choropleth(df_country_sales, locations='Country', locationmode='country names', color='Sales',
                             color_continuous_scale='Viridis', title='Mapa de Vendas de Video Games por País',
                             labels={'Sales': 'Vendas (em milhões)', 'Country': 'País'})
    )
])

if __name__ == '__main__':
    app.run_server(debug=False)
