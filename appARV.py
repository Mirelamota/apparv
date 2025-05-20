import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Primeiro comando do Streamlit: configuração da página
st.set_page_config(page_title="Relatórios de Vendas", layout="wide")

# Estilos CSS personalizados
st.markdown("""
<style>
    .reportview-container {
        background-color: #f9f9f9;
    }
    .kpi-box {
        padding: 20px;
        border-radius: 10px;
        color: white;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        margin: 10px;
    }
    .kpi-faturamento { background-color: #1f77b4; }
    .kpi-vendas { background-color: #2ca02c; }
    .kpi-ticket { background-color: #ff7f0e; }

    .intro-box {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Função para gerar modelo CSV já preenchido com dados fictícios de dois meses
def gerar_modelo_preenchido():
    dados_exemplo = {
        'data_venda': [
            '2024-01-05', '2024-01-06', '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10',
            '2024-02-01', '2024-02-02', '2024-02-03', '2024-02-04', '2024-02-05', '2024-02-06'
        ],
        'produto': [
            'Caderno', 'Caneta Azul', 'Mochila Escolar', 'Lápis', 'Caderno de Desenho', 'Caneta Vermelha',
            'Caneta Preta', 'Post-it', 'Tesoura', 'Caneta Azul', 'Caderno Universitário', 'Caneta Verde'
        ],
        'quantidade': [10, 50, 5, 30, 8, 40, 60, 20, 10, 70, 15, 35],
        'valor_total': [15.00, 2.00, 120.00, 1.50, 25.00, 2.00,
                        2.00, 10.00, 8.00, 2.00, 20.00, 2.00],
        'categoria': ['Papelaria', 'Acessórios', 'Papelaria', 'Acessórios', 'Papelaria', 'Acessórios',
                      'Acessórios', 'Papelaria', 'Papelaria', 'Acessórios', 'Papelaria', 'Acessórios'],
        'custo': [8.00, 1.00, 80.00, 0.70, 15.00, 1.00,
                  1.00, 6.00, 5.00, 1.00, 12.00, 1.00]
    }
    return pd.DataFrame(dados_exemplo).to_csv(index=False, sep=';', decimal=',')

# Função para gerar modelo vazio
def gerar_modelo_vazio():
    return pd.DataFrame(columns=['data_venda', 'produto', 'quantidade', 'valor_total', 'categoria', 'custo (opcional)']).to_csv(index=False, sep=';', decimal=',')

# Tela Inicial com Logo e Descrição
def tela_inicial():
    st.markdown("""
    <div class="intro-box">
        <h1>📊 Automatizador de Relatórios de Vendas</h1>
        <p>Bem-vindo ao seu painel de análise de vendas!</p>
        <p>Carregue seus dados de vendas e gere relatórios completos em minutos.</p>
        <ul style="text-align:left;">
            <li>🔍 Visualize os produtos mais vendidos</li>
            <li>📅 Veja a sazonalidade das vendas</li>
            <li>💰 Analise lucratividade e margem de lucro</li>
            <li>📈 Acompanhe o crescimento mensal</li>
        </ul>
        <p>Use os modelos na barra lateral para começar!</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# Barra lateral - Modelos
st.sidebar.header("📥 Modelos de Arquivo CSV")
with st.sidebar.expander("✅ Modelo Preenchido"):
    st.markdown("Use como exemplo para preenchimento.")
    st.download_button("📥 Baixar Modelo Preenchido", gerar_modelo_preenchido(), "modelo_preenchido.csv", "text/csv")

with st.sidebar.expander("📄 Modelo Vazio"):
    st.markdown("Baixe um modelo vazio para preencher do zero.")
    st.download_button("📥 Baixar Modelo Vazio", gerar_modelo_vazio(), "modelo_vazio.csv", "text/csv")

# Tela inicial
tela_inicial()

# Upload do arquivo
uploaded_file = st.file_uploader("📁 Carregue sua planilha de vendas (CSV ou Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=';', decimal=',')
        else:
            df = pd.read_excel(uploaded_file)

        # Verificar colunas obrigatórias
        colunas_obrigatorias = ['data_venda', 'produto', 'quantidade', 'valor_total', 'categoria']
        for col in colunas_obrigatorias:
            if col not in df.columns:
                st.error(f"⚠️ A coluna obrigatória '{col}' não foi encontrada no arquivo.")
                st.stop()

        # Converter e limpar dados
        df['data_venda'] = pd.to_datetime(df['data_venda'], errors='coerce')
        df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce')
        df['valor_total'] = pd.to_numeric(df['valor_total'], errors='coerce')
        df = df.dropna(subset=['data_venda', 'quantidade', 'valor_total'])

        # Filtro por data
        st.sidebar.subheader("📅 Filtro por Período")
        min_data = df['data_venda'].min().date()
        max_data = df['data_venda'].max().date()
        data_inicio, data_fim = st.sidebar.date_input("Selecione o período", [min_data, max_data])
        filtered_df = df[(df['data_venda'] >= pd.to_datetime(data_inicio)) & (df['data_venda'] <= pd.to_datetime(data_fim))]

        # Filtro por categoria
        categorias = filtered_df['categoria'].unique()
        categoria_selecionada = st.sidebar.multiselect("🔍 Filtros por Categoria", categorias, default=categorias)
        filtered_df = filtered_df[filtered_df['categoria'].isin(categoria_selecionada)]

        # Abas principais
        tab_resumo, tab_produtos, tab_sazonalidade, tab_lucratividade, tab_crescimento = st.tabs([
            "📊 Resumo", "📦 Produtos", "📅 Sazonalidade", "📊 Margem de Lucro", "📈 Crescimento"
        ])

        with tab_resumo:
            faturamento_total = filtered_df['valor_total'].sum()
            num_vendas = len(filtered_df)
            ticket_medio = faturamento_total / num_vendas if num_vendas > 0 else 0

            col1, col2, col3 = st.columns(3)
            col1.markdown(f"<div class='kpi-box kpi-faturamento'>R$ {faturamento_total:.2f}<br>Faturamento Total</div>",
                          unsafe_allow_html=True)
            col2.markdown(f"<div class='kpi-box kpi-vendas'>{num_vendas}<br>Nº de Vendas</div>",
                          unsafe_allow_html=True)
            col3.markdown(f"<div class='kpi-box kpi-ticket'>R$ {ticket_medio:.2f}<br>Ticket Médio</div>",
                          unsafe_allow_html=True)

        with tab_produtos:
            top_produtos = filtered_df.groupby('produto')['quantidade'].sum().sort_values(ascending=False).head(10)
            fig = px.bar(top_produtos, x=top_produtos.values, y=top_produtos.index, orientation='h',
                         title="Top 10 Produtos Mais Vendidos",
                         labels={'x': 'Quantidade Vendida', 'y': 'Produto'})
            st.plotly_chart(fig, use_container_width=True)

        with tab_sazonalidade:
            vendas_por_dia = filtered_df.resample('D', on='data_venda')['valor_total'].sum()
            fig = px.line(vendas_por_dia, x=vendas_por_dia.index, y=vendas_por_dia.values,
                          title="Vendas ao longo do Tempo", labels={'x': 'Data', 'y': 'Valor Total (R$)'})
            st.plotly_chart(fig, use_container_width=True)

        with tab_lucratividade:
            if 'custo' in filtered_df.columns:
                # Calcular lucro e margem de lucro
                filtered_df['lucro'] = filtered_df['valor_total'] - filtered_df['custo']
                filtered_df['margem_lucro'] = (filtered_df['lucro'] / filtered_df['valor_total']) * 100
                margens = filtered_df.groupby('produto', as_index=False)['margem_lucro'].mean()
                margens = margens.sort_values(by='margem_lucro', ascending=False)

                # Gráfico de margem de lucro
                fig = px.bar(margens.head(10), x='margem_lucro', y='produto', orientation='h',
                             title="📊 Margem de Lucro por Produto",
                             labels={'margem_lucro': 'Margem de Lucro (%)', 'produto': 'Produto'},
                             range_x=[0, 100])
                st.plotly_chart(fig, use_container_width=True)

                # Tabela com detalhes
                tabela_margem = margens.copy()
                tabela_margem['margem_lucro'] = tabela_margem['margem_lucro'].round(2)
                tabela_margem.rename(columns={'margem_lucro': 'Margem de Lucro (%)'}, inplace=True)
                st.write("📌 **Detalhe da Margem de Lucro por Produto:**")
                st.dataframe(tabela_margem, use_container_width=True)

            else:
                st.info("ℹ️ Para ver a margem de lucro, inclua a coluna 'custo' no seu arquivo.")

        with tab_crescimento:
            if 'custo' in filtered_df.columns:
                df_mensal = filtered_df.resample('M', on='data_venda').agg(
                    faturamento=('valor_total', 'sum'),
                    lucro=('lucro', 'sum')
                ).reset_index()
                df_mensal['mês'] = df_mensal['data_venda'].dt.strftime('%b %Y')

                fig = px.line(df_mensal, x='mês', y=['faturamento', 'lucro'],
                              title="Faturamento e Lucro Mensal",
                              labels={'value': 'Valor (R$)', 'variable': 'Tipo'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("ℹ️ Adicione a coluna 'custo' para visualizar o crescimento mensal.")

        # Exportação do relatório
        st.sidebar.subheader("📦 Exportar Relatório")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            top_produtos = filtered_df.groupby('produto')['quantidade'].sum().sort_values(ascending=False).head(10)
            top_produtos.to_excel(writer, sheet_name="Top Produtos")
            if 'custo' in filtered_df.columns:
                margens.to_excel(writer, sheet_name="Margem de Lucro", index=False)
                df_mensal.to_excel(writer, sheet_name="Crescimento Mensal", index=False)
        buffer.seek(0)

        st.sidebar.download_button(
            label="⬇️ Baixar Relatório em Excel",
            data=buffer,
            file_name="relatorio_vendas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, carregue um arquivo ou baixe o modelo acima para começar.")