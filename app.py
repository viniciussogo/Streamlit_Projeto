
# Imports
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# -----------------------------
# Funções Utilitárias
# -----------------------------

@st.cache_data(show_spinner=True)
def load_data(file):
    """
    Carrega dados de um arquivo CSV ou Excel.
    """
    try:
        if file.name.endswith('.csv'):
            data = pd.read_csv(file, sep=';')
        elif file.name.endswith('.xlsx'):
            data = pd.read_excel(file)
        else:
            st.error("Formato de arquivo não suportado. Envie um CSV ou Excel.")
            return None
        return data
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

@st.cache_data
def multiselect_filter(df, column, selected_values):
    """
    Filtra um DataFrame baseado nos valores selecionados.
    """
    if 'all' in selected_values:
        return df
    return df[df[column].isin(selected_values)].reset_index(drop=True)

@st.cache_data
def to_excel(df):
    """
    Converte um DataFrame em um arquivo Excel em memória.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output

# -----------------------------
# Função Principal
# -----------------------------
def main():
    # Configuração da página
    st.set_page_config(
        page_title='Telemarketing Analysis',
        page_icon=None,  # Adicione um path se quiser um ícone
        layout="wide",
        initial_sidebar_state='expanded'
    )

    # Título
    st.write('# Telemarketing Analysis')
    st.markdown("---")

    # Imagem na barra lateral
    try:
        image = Image.open(r"C:\Users\winga\Downloads\Material_de_apoio_M19_Cientista de Dados\img\Bank-Branding.jpg")
        st.sidebar.image(image)
    except:
        st.sidebar.warning("Imagem não encontrada.")

    # Upload de arquivo
    st.sidebar.write("## Suba o arquivo")
    data_file = st.sidebar.file_uploader("Bank marketing data", type=['csv', 'xlsx'])

    if data_file:
        bank_raw = load_data(data_file)
        if bank_raw is None:
            return

        bank = bank_raw.copy()

        st.write('## Antes dos filtros')
        st.write(bank.head())

        with st.sidebar.form(key='filter_form'):
            graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))

            # IDADES
            min_age, max_age = int(bank.age.min()), int(bank.age.max())
            idades = st.slider('Idade', min_value=min_age, max_value=max_age, value=(min_age, max_age), step=1)

            # Filtros múltiplos
            filtros = {
                'job': 'Profissão',
                'marital': 'Estado civil',
                'default': 'Default?',
                'housing': 'Tem financiamento imob?',
                'loan': 'Tem empréstimo?',
                'contact': 'Meio de contato',
                'month': 'Mês do contato',
                'day_of_week': 'Dia da semana'
            }

            selections = {}
            for col, label in filtros.items():
                values = bank[col].dropna().unique().tolist()
                values.append('all')
                selections[col] = st.multiselect(label, values, ['all'])

            submit_button = st.form_submit_button(label='Aplicar')

        # Aplicação dos filtros
        bank = bank.query("age >= @idades[0] and age <= @idades[1]")
        for col, selected in selections.items():
            bank = multiselect_filter(bank, col, selected)

        # Verificação de DataFrame vazio
        if bank.empty:
            st.warning("Nenhum dado encontrado com os filtros selecionados.")
            return

        # Tabela filtrada
        st.write('## Após os filtros')
        st.write(bank.head())

        df_xlsx = to_excel(bank)
        st.download_button(label='📥 Download tabela filtrada em EXCEL', data=df_xlsx, file_name='bank_filtered.xlsx')
        st.markdown("---")

        # Proporções
        bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).sort_index().to_frame(name='y') * 100
        bank_target_perc = bank.y.value_counts(normalize=True).sort_index().to_frame(name='y') * 100

        col1, col2 = st.columns(2)
        col1.write('### Proporção original')
        col1.write(bank_raw_target_perc)
        col1.download_button('📥 Download', data=to_excel(bank_raw_target_perc), file_name='bank_raw_y.xlsx')

        col2.write('### Proporção da tabela com filtros')
        col2.write(bank_target_perc)
        col2.download_button('📥 Download', data=to_excel(bank_target_perc), file_name='bank_y.xlsx')

        st.markdown("---")
        st.write('## Proporção de aceite')

        # Gráficos
        fig, ax = plt.subplots(1, 2, figsize=(10, 4))

        if graph_type == 'Barras':
            if not bank_raw_target_perc.empty:
                sns.barplot(x=bank_raw_target_perc.index, y='y', data=bank_raw_target_perc, ax=ax[0])
                if ax[0].containers:
                    ax[0].bar_label(ax[0].containers[0])
                ax[0].set_title('Dados brutos', fontweight="bold")

            if not bank_target_perc.empty:
                sns.barplot(x=bank_target_perc.index, y='y', data=bank_target_perc, ax=ax[1])
                if ax[1].containers:
                    ax[1].bar_label(ax[1].containers[0])
                ax[1].set_title('Dados filtrados', fontweight="bold")
        else:
            bank_raw_target_perc.plot(kind='pie', y='y', autopct='%.2f%%', ax=ax[0])
            ax[0].set_title('Dados brutos', fontweight="bold")
            ax[0].set_ylabel('')

            bank_target_perc.plot(kind='pie', y='y', autopct='%.2f%%', ax=ax[1])
            ax[1].set_title('Dados filtrados', fontweight="bold")
            ax[1].set_ylabel('')

        st.pyplot(fig)

# -----------------------------
# Executa a aplicação
# -----------------------------
if __name__ == '__main__':
    # Configura o estilo dos gráficos
    custom_params = {"axes.spines.right": False, "axes.spines.top": False}
    sns.set_theme(style="ticks", rc=custom_params)

    main()
