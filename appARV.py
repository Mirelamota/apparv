import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configurações iniciais do Streamlit
st.title("Automatizador de Relatórios de Vendas")
st.markdown("Carregue seus dados de vendas e gere relatórios personalizados!")

# Upload de arquivo
uploaded_file = st.file_uploader("Carregue sua planilha de vendas (Excel/CSV)", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Ler os dados do arquivo
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Verificar se as colunas obrigatórias estão presentes
        colunas_obrigatorias = ['produto', 'quantidade', 'valor_total', 'categoria']
        if not all(col in df.columns for col in colunas_obrigatorias):
            st.error(f"O arquivo carregado não contém todas as colunas obrigatórias: {', '.join(colunas_obrigatorias)}")
            st.stop()

        # Filtros
        st.sidebar.header("Filtros")

        categorias = df['categoria'].unique()
        categoria_selecionada = st.sidebar.multiselect("Selecione Categorias", categorias, default=categorias)

        # Filtragem dos dados
        filtered_df = df[df['categoria'].isin(categoria_selecionada)] if categoria_selecionada else df

        # Botão para gerar relatórios
        if st.button("Gerar Relatórios"):
            st.subheader("Relatório de Vendas")

            # 1. Itens mais vendidos
            top_produtos = filtered_df.groupby('produto')['quantidade'].sum().sort_values(ascending=False).head(10)
            st.write("### Top 10 Produtos Mais Vendidos")
            fig_top_produtos, ax_top_produtos = plt.subplots()
            top_produtos.plot(kind='bar', ax=ax_top_produtos, color='skyblue')
            ax_top_produtos.set_title("Top 10 Produtos Mais Vendidos")
            ax_top_produtos.set_ylabel("Quantidade Vendida")
            ax_top_produtos.set_xlabel("Produto")
            st.pyplot(fig_top_produtos)

            # 2. Produtos mais rentáveis
            if 'custo' in filtered_df.columns:
                filtered_df['rentabilidade'] = filtered_df['quantidade'] * (filtered_df['valor_total'] - filtered_df['custo'])
                produtos_rentaveis = filtered_df.groupby('produto')['rentabilidade'].sum().sort_values(ascending=False).head(10)
                st.write("### Produtos Mais Rentáveis")
                fig_rentaveis, ax_rentaveis = plt.subplots()
                produtos_rentaveis.plot(kind='bar', ax=ax_rentaveis, color='lightgreen')
                ax_rentaveis.set_title("Produtos Mais Rentáveis")
                ax_rentaveis.set_ylabel("Rentabilidade Total (R$)")
                ax_rentaveis.set_xlabel("Produto")
                st.pyplot(fig_rentaveis)

            # 3. Lucratividade por categoria
            if 'custo' in filtered_df.columns:
                filtered_df['lucro'] = filtered_df['valor_total'] - filtered_df['custo']
                lucratividade = filtered_df.groupby('categoria')['lucro'].sum()
                st.write("### Lucratividade por Categoria")
                fig_lucratividade, ax_lucratividade = plt.subplots()
                lucratividade.plot(kind='bar', ax=ax_lucratividade, color='orange')
                ax_lucratividade.set_title("Lucratividade por Categoria")
                ax_lucratividade.set_ylabel("Lucro Total (R$)")
                ax_lucratividade.set_xlabel("Categoria")
                st.pyplot(fig_lucratividade)

            # 4. Análise de Categorias (Participação no Faturamento)
            faturamento_por_categoria = filtered_df.groupby('categoria')['valor_total'].sum()
            participacao_faturamento = faturamento_por_categoria / faturamento_por_categoria.sum() * 100
            st.write("### Participação no Faturamento por Categoria")
            fig_participacao, ax_participacao = plt.subplots()
            ax_participacao.pie(participacao_faturamento, labels=participacao_faturamento.index, autopct='%1.1f%%', startangle=90)
            ax_participacao.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            ax_participacao.set_title("Participação no Faturamento (%)")
            st.pyplot(fig_participacao)

            # 5. Margem de Lucro por Produto
            if 'custo' in filtered_df.columns:
                filtered_df['margem_lucro'] = (filtered_df['valor_total'] - filtered_df['custo']) / filtered_df['valor_total']
                margem_lucro_por_produto = filtered_df.groupby('produto')['margem_lucro'].mean().sort_values(ascending=False).head(10)
                st.write("### Margem de Lucro por Produto")
                fig_margem, ax_margem = plt.subplots()
                margem_lucro_por_produto.plot(kind='bar', ax=ax_margem, color='salmon')
                ax_margem.set_title("Margem de Lucro Média por Produto")
                ax_margem.set_ylabel("Margem de Lucro (%)")
                ax_margem.set_xlabel("Produto")
                st.pyplot(fig_margem)

            # Resumo geral
            total_vendas = filtered_df['valor_total'].sum()
            ticket_medio = filtered_df['valor_total'].mean()
            st.write(f"**Total de Vendas:** R$ {total_vendas:.2f}")
            st.write(f"**Ticket Médio:** R$ {ticket_medio:.2f}")

            # Download do relatório
            st.subheader("Baixar Relatório")
            with st.spinner("Gerando arquivo Excel..."):
                with pd.ExcelWriter("relatorio_vendas.xlsx", engine="openpyxl") as writer:
                    top_produtos.to_excel(writer, sheet_name="Top Produtos")
                    if 'custo' in filtered_df.columns:
                        produtos_rentaveis.to_excel(writer, sheet_name="Produtos Rentáveis")
                        lucratividade.to_excel(writer, sheet_name="Lucratividade")
                        participacao_faturamento.to_excel(writer, sheet_name="Participação Faturamento")
                        margem_lucro_por_produto.to_excel(writer, sheet_name="Margem Lucro Produto")
                st.success("Relatório gerado com sucesso!")
            with open("relatorio_vendas.xlsx", "rb") as file:
                st.download_button(
                    label="Baixar Relatório",
                    data=file,
                    file_name="relatorio_vendas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, carregue um arquivo para continuar.")