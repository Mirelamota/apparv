import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# Configuração da página
st.set_page_config(page_title="Relatórios de Vendas", layout="wide")
st.title("📊 Automatizador de Relatórios de Vendas")
st.markdown("Carregue seus dados de vendas e gere relatórios personalizados!")

# Função para gerar modelo CSV
def gerar_modelo():
    modelo = pd.DataFrame(columns=[
        'data_venda', 'produto', 'quantidade', 'valor_total', 'categoria', 'custo (opcional)'
    ])
    return modelo.to_csv(index=False, sep=';', decimal=',')

# Barra lateral com modelo para download
st.sidebar.header("📥 Modelo de Arquivo CSV")
with st.sidebar.expander("Baixe o modelo aqui"):
    st.markdown("""
    Utilize o modelo abaixo para garantir que seu arquivo tenha as colunas corretas:
    
    - **Colunas obrigatórias:** data_venda, produto, quantidade, valor_total, categoria  
    - **Coluna opcional:** custo (para análise financeira)
    """)
    csv_modelo = gerar_modelo()
    st.download_button(
        label="Baixar Modelo CSV",
        data=csv_modelo,
        file_name="modelo_relatorio_vendas.csv",
        mime="text/csv"
    )

# Upload do arquivo
uploaded_file = st.file_uploader("📁 Carregue sua planilha de vendas (CSV ou Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Ler o arquivo
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=';', decimal=',')
        else:
            df = pd.read_excel(uploaded_file)

        # Verificar se tem as colunas necessárias
        colunas_obrigatorias = ['data_venda', 'produto', 'quantidade', 'valor_total', 'categoria']
        for col in colunas_obrigatorias:
            if col not in df.columns:
                st.error(f"⚠️ A coluna obrigatória '{col}' não foi encontrada no arquivo.")
                st.stop()

        # Garantir que os tipos estejam corretos
        df['data_venda'] = pd.to_datetime(df['data_venda'], errors='coerce')
        df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce')
        df['valor_total'] = pd.to_numeric(df['valor_total'], errors='coerce')

        # Remover linhas com dados inválidos
        df = df.dropna(subset=['data_venda', 'quantidade', 'valor_total'])

        # Filtro por categoria
        st.sidebar.header("🔍 Filtros")
        categorias = df['categoria'].unique()
        categoria_selecionada = st.sidebar.multiselect("Selecione Categorias", categorias, default=categorias)
        filtered_df = df[df['categoria'].isin(categoria_selecionada)] if categoria_selecionada else df

        # Botão para gerar relatórios
        if st.button("📈 Gerar Relatórios"):

            # Resumo Geral
            st.subheader("📄 Resumo Geral dos Relatórios")

            faturamento_total = filtered_df['valor_total'].sum()
            num_vendas = len(filtered_df)
            ticket_medio = faturamento_total / num_vendas if num_vendas > 0 else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Faturamento Total", f"R$ {faturamento_total:.2f}")
            col2.metric("🧾 Número de Vendas", num_vendas)
            col3.metric("🔢 Ticket Médio", f"R$ {ticket_medio:.2f}")

            # Produtos Mais Vendidos
            top_produtos = filtered_df.groupby('produto')['quantidade'].sum().sort_values(ascending=False).head(10)
            st.write("### 🏆 Top 10 Produtos Mais Vendidos")
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(x=top_produtos.values, y=top_produtos.index, palette="Blues_d", ax=ax)
            ax.set_xlabel("Quantidade Vendida")
            ax.set_ylabel("Produto")
            ax.set_title("Top 10 Produtos Mais Vendidos")
            st.pyplot(fig)

            # Lucratividade por Produto (se houver custo)
            if 'custo' in filtered_df.columns:
                filtered_df['lucro'] = filtered_df['valor_total'] - filtered_df['custo']
                filtered_df['rentabilidade'] = filtered_df['lucro'] * filtered_df['quantidade']
                rentaveis = filtered_df.groupby('produto')['rentabilidade'].sum().sort_values(ascending=False).head(10)
                st.write("### 💸 Produtos Mais Rentáveis")
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.barplot(x=rentaveis.values, y=rentaveis.index, palette="Greens_d", ax=ax)
                ax.set_xlabel("Lucro Total (R$)")
                ax.set_ylabel("Produto")
                ax.set_title("Produtos Mais Rentáveis")
                st.pyplot(fig)

            # Sazonalidade de Vendas
            if not filtered_df.empty and 'data_venda' in filtered_df.columns:
                vendas_por_dia = filtered_df.resample('D', on='data_venda')['valor_total'].sum()
                if not vendas_por_dia.empty:
                    st.write("### 📅 Sazonalidade de Vendas (por dia)")
                    fig, ax = plt.subplots(figsize=(10, 4))
                    vendas_por_dia.plot(kind='line', ax=ax, title="Vendas ao longo do tempo", ylabel="Valor Total (R$)", xlabel="Data")
                    ax.grid(True)
                    st.pyplot(fig)
                else:
                    st.warning("⚠️ Não há dados suficientes para mostrar a sazonalidade.")

            # Geração do relatório em Excel
            st.subheader("📦 Baixar Relatório")
            with st.spinner("Gerando arquivo Excel..."):
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    top_produtos.to_excel(writer, sheet_name="Top Produtos")
                    if 'custo' in filtered_df.columns:
                        rentaveis.to_excel(writer, sheet_name="Produtos Rentáveis")
                    if not filtered_df.empty and 'data_venda' in filtered_df.columns:
                        vendas_por_dia.to_excel(writer, sheet_name="Sazonalidade")
                buffer.seek(0)
                st.success("✅ Relatório pronto!")
                st.download_button(
                    label="⬇️ Baixar Relatório em Excel",
                    data=buffer,
                    file_name="relatorio_vendas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, carregue um arquivo ou baixe o modelo acima para começar.")