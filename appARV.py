import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configurações iniciais do Streamlit
st.title("Automatizador de Relatórios de Vendas")
st.markdown("Carregue seus dados de vendas e gere relatórios personalizados!")

# Upload de arquivo
uploaded_file = st.file_uploader("Carregue sua planilha de vendas (Excel/CSV)", type=["csv", "xlsx"])

# Verificar se um arquivo foi carregado
if uploaded_file is not None:
    # Ler os dados do arquivo
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Pré-processamento básico
        df['data'] = pd.to_datetime(df['data'], errors='coerce')  # Converter coluna de data
        df.dropna(subset=['data'], inplace=True)  # Remover linhas com datas inválidas

        # Verificar se as colunas obrigatórias estão presentes
        colunas_obrigatorias = ['data', 'produto', 'quantidade', 'valor_total', 'categoria']
        if not all(col in df.columns for col in colunas_obrigatorias):
            st.error(f"O arquivo carregado não contém todas as colunas obrigatórias: {', '.join(colunas_obrigatorias)}")
            st.stop()

        # Filtros
        st.sidebar.header("Filtros")
        data_inicial = st.sidebar.date_input("Data Inicial", df['data'].min().date())
        data_final = st.sidebar.date_input("Data Final", df['data'].max().date())

        categorias = df['categoria'].unique()
        categoria_selecionada = st.sidebar.multiselect("Selecione Categorias", categorias, default=categorias)

        # Filtragem dos dados
        filtered_df = df[
            (df['data'].dt.date >= data_inicial) &
            (df['data'].dt.date <= data_final) &
            (df['categoria'].isin(categoria_selecionada))
        ]

        # Botão para gerar relatórios
        if st.button("Gerar Relatórios"):
            st.subheader("Relatório de Vendas")

            # Itens mais vendidos
            top_produtos = filtered_df.groupby('produto')['quantidade'].sum().sort_values(ascending=False).head(10)
            st.write("### Top 10 Produtos Mais Vendidos")
            st.bar_chart(top_produtos)

            # Horários de pico
            filtered_df['hora'] = filtered_df['data'].dt.hour
            horarios_pico = filtered_df.groupby('hora')['valor_total'].sum().sort_values(ascending=False)
            st.write("### Horários de Pico")
            st.line_chart(horarios_pico)

            # Lucratividade por categoria
            if 'custo' in df.columns:
                filtered_df['lucro'] = filtered_df['valor_total'] - filtered_df['custo']
                lucratividade = filtered_df.groupby('categoria')['lucro'].sum()
                st.write("### Lucratividade por Categoria")
                st.bar_chart(lucratividade)

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
                    horarios_pico.to_excel(writer, sheet_name="Horários de Pico")
                    if 'custo' in df.columns:
                        lucratividade.to_excel(writer, sheet_name="Lucratividade")
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