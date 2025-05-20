import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# Configuração inicial
st.set_page_config(page_title="Relatórios de Vendas", layout="wide")
st.title("📊 Automatizador de Relatórios de Vendas")
st.markdown("Carregue seus dados de vendas e gere relatórios personalizados!")

# Função para criar modelo CSV
def gerar_modelo():
    modelo = pd.DataFrame(columns=['produto', 'quantidade', 'valor_total', 'categoria', 'custo (opcional)'])
    return modelo.to_csv(index=False, sep=';', decimal=',')

# Seção de modelo CSV
st.sidebar.header("📥 Modelo de Arquivo CSV")
with st.sidebar.expander("Baixe o modelo aqui"):
    st.markdown("""
    Utilize o modelo abaixo para garantir que seu arquivo tenha as colunas corretas:
    - **Colunas obrigatórias:** produto, quantidade, valor_total, categoria
    - **Coluna opcional:** custo (para análise financeira)
    """)
    csv_modelo = gerar_modelo()
    st.download_button(
        label="Baixar Modelo CSV",
        data=csv_modelo,
        file_name="modelo_relatorio_vendas.csv",
        mime="text/csv"
    )

# Upload de arquivo
uploaded_file = st.file_uploader("📁 Carregue sua planilha de vendas (Excel/CSV)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Ler o arquivo
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=';', decimal=',')
        else:
            df = pd.read_excel(uploaded_file)

        # Verificar colunas obrigatórias
        colunas_obrigatorias = ['produto', 'quantidade', 'valor_total', 'categoria']
        if not all(col in df.columns for col in colunas_obrigatorias):
            st.error(f"O arquivo carregado não contém todas as colunas obrigatórias: {', '.join(colunas_obrigatorias)}")
            st.stop()

        # Filtro de categorias
        st.sidebar.header("🔍 Filtros")
        categorias = df['categoria'].unique()
        categoria_selecionada = st.sidebar.multiselect("Selecione Categorias", categorias, default=categorias)
        filtered_df = df[df['categoria'].isin(categoria_selecionada)] if categoria_selecionada else df

        # Botão para gerar relatório
        if st.button("📈 Gerar Relatórios"):
            st.subheader("📄 Relatório de Vendas")

            # Gráfico 1: Produtos mais vendidos
            top_produtos = filtered_df.groupby('produto')['quantidade'].sum().sort_values(ascending=False).head(10)
            st.write("### Top 10 Produtos Mais Vendidos")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x=top_produtos.values, y=top_produtos.index, palette="Blues_d", ax=ax)
            ax.set_xlabel("Quantidade Vendida")
            ax.set_ylabel("Produto")
            ax.set_title("Top 10 Produtos Mais Vendidos")
            st.pyplot(fig)

            # Gráfico 2: Produtos mais rentáveis (requer 'custo')
            if 'custo' in filtered_df.columns:
                filtered_df['rentabilidade'] = filtered_df['quantidade'] * (filtered_df['valor_total'] - filtered_df['custo'])
                produtos_rentaveis = filtered_df.groupby('produto')['rentabilidade'].sum().sort_values(ascending=False).head(10)
                st.write("### Produtos Mais Rentáveis")
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(x=produtos_rentaveis.values, y=produtos_rentaveis.index, palette="Greens_d", ax=ax)
                ax.set_xlabel("Rentabilidade Total (R$)")
                ax.set_ylabel("Produto")
                ax.set_title("Produtos Mais Rentáveis")
                st.pyplot(fig)

            # Gráfico 3: Lucratividade por categoria (requer 'custo')
            if 'custo' in filtered_df.columns:
                filtered_df['lucro'] = filtered_df['valor_total'] - filtered_df['custo']
                lucratividade = filtered_df.groupby('categoria')['lucro'].sum()
                st.write("### Lucratividade por Categoria")
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.barplot(x=lucratividade.values, y=lucratividade.index, palette="Oranges_d", ax=ax)
                ax.set_xlabel("Lucro Total (R$)")
                ax.set_ylabel("Categoria")
                ax.set_title("Lucratividade por Categoria")
                st.pyplot(fig)

            # Gráfico 4: Participação no faturamento
            faturamento_por_categoria = filtered_df.groupby('categoria')['valor_total'].sum()
            participacao_faturamento = faturamento_por_categoria / faturamento_por_categoria.sum() * 100
            st.write("### Participação no Faturamento por Categoria")
            fig, ax = plt.subplots(figsize=(7, 7))
            ax.pie(participacao_faturamento, labels=participacao_faturamento.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            ax.set_title("Participação (%)")
            st.pyplot(fig)

            # Gráfico 5: Margem de lucro por produto (requer 'custo')
            if 'custo' in filtered_df.columns:
                filtered_df['margem_lucro'] = (filtered_df['valor_total'] - filtered_df['custo']) / filtered_df['valor_total']
                margem_lucro_por_produto = filtered_df.groupby('produto')['margem_lucro'].mean().sort_values(ascending=False).head(10)
                st.write("### Margem de Lucro Média por Produto")
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(x=margem_lucro_por_produto.values * 100, y=margem_lucro_por_produto.index, palette="Reds_d", ax=ax)
                ax.set_xlabel("Margem de Lucro (%)")
                ax.set_ylabel("Produto")
                ax.set_title("Margem de Lucro Média por Produto")
                st.pyplot(fig)

            # Resumo geral
            total_vendas = filtered_df['valor_total'].sum()
            ticket_medio = filtered_df['valor_total'].mean()
            st.write(f"💰 **Total de Vendas:** R$ {total_vendas:.2f}")
            st.write(f"🧾 **Ticket Médio:** R$ {ticket_medio:.2f}")

            # Geração de relatório em Excel
            st.subheader("📦 Baixar Relatório")
            with st.spinner("Gerando arquivo Excel..."):
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    top_produtos.to_excel(writer, sheet_name="Top Produtos")
                    if 'custo' in filtered_df.columns:
                        produtos_rentaveis.to_excel(writer, sheet_name="Produtos Rentáveis")
                        lucratividade.to_excel(writer, sheet_name="Lucratividade")
                        participacao_faturamento.to_excel(writer, sheet_name="Participação Faturamento")
                        margem_lucro_por_produto.to_excel(writer, sheet_name="Margem Lucro Produto")
                buffer.seek(0)
                st.success("✅ Relatório gerado com sucesso!")
                st.download_button(
                    label="⬇️ Baixar Relatório",
                    data=buffer,
                    file_name="relatorio_vendas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, carregue um arquivo ou baixe o modelo acima para começar.")