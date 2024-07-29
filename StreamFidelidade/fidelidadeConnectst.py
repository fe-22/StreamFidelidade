import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date, datetime
import sqlite3
import os

# Verificar se a imagem existe e exibi-la
image_path = "logo_church.png"
if os.path.exists(image_path):
    st.image(image_path, width=100)  # ajuste o tamanho da imagem
else:
    st.error(f"Imagem '{image_path}' não encontrada.")

# Adaptadores de data para SQLite
def adapt_date(isodate):
    return isodate.isoformat()

def convert_date(date_bytes):
    return datetime.strptime(date_bytes.decode("utf-8"), "%Y-%m-%d").date()

sqlite3.register_adapter(date, adapt_date)
sqlite3.register_converter("DATE", convert_date)

# Conexão com o banco de dados
conn = sqlite3.connect('dados.db', detect_types=sqlite3.PARSE_DECLTYPES)
cursor = conn.cursor()

# Criação da tabela se não existir
cursor.execute('''
  CREATE TABLE IF NOT EXISTS membros (
    id INTEGER PRIMARY KEY,
    nome TEXT,
    data_nascimento DATE,
    estado_civil TEXT,
    conjugue TEXT,
    filhos TEXT,
    consagrado TEXT,
    local_consagracao TEXT,
    data_consagracao DATE,
    cargo TEXT
  );
''')
conn.commit()

# Verifica e adiciona colunas, se não existirem
cursor.execute("PRAGMA table_info(membros);")
colunas = [coluna[1] for coluna in cursor.fetchall()]

novas_colunas = [
    ("profissao", "TEXT"),
    ("endereco", "TEXT"),
    ("telefone", "TEXT"),
    ("whatsapp", "TEXT"),
    ("data_chegada", "DATE"),
    ("cursou_teologia", "TEXT"),
    ("grau_teologia", "TEXT"),
    ("observacoes", "TEXT")
]

for coluna, tipo in novas_colunas:
    if coluna not in colunas:
        cursor.execute(f"ALTER TABLE membros ADD COLUMN {coluna} {tipo};")
        conn.commit()

# Adicionar CSS para mudar a cor de fundo e clarear os títulos
st.markdown(
    """
    <style>
    body {
        background-color: #000;
    }
    .stApp {
        background-color: #000;
    }
    .stTextInput label, .stDateInput label, .stSelectbox label, .stRadio label, .stNumberInput label, .stDownloadButton label {
        color: white;
    }
    .logo {
        width: 100px;
        margin-bottom: 50px;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: black;
        color: white;
        text-align: center;
        padding: 10px;
    }
    h1, h2, h3 {
        color: #FFFFFF;  /* Clarear títulos */
    }
        .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: black;
        color: white;
        text-align: center;
        padding: 5px;  /* Diminuir o padding para ajustar a altura */
        font-size: 12px;  /* Diminuir o tamanho da fonte */
    }
    h1, h2, h3 {
        color: #FFFFFF;  /* Clarear títulos */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título da aplicação
st.title("ADFIDELIDADE")
st.header("Pastor Presidente: Eudes Angelo")

st.header("Cadastro de Membros")

# Cria um contêiner de formulário
form_container = st.container()

# Adiciona campos ao formulário
with form_container:
    nome = st.text_input("Nome")
    data_nascimento = st.date_input("Data de Nascimento", min_value=date(1900, 1, 1), max_value=date.today())
    estado_civil = st.selectbox("Estado Civil", ["Solteiro", "Casado", "Viúvo", "Divorciado"])
    profissao = st.text_input("Profissão")
    endereco = st.text_input("Endereço")
    telefone = st.text_input("Telefone")
    whatsapp = st.radio("O telefone tem WhatsApp?", ("Sim", "Não"))
    data_chegada = st.date_input("Data que chegou na igreja", min_value=date(1900, 1, 1), max_value=date.today())

    conjugue = ""
    filhos = []
    
    if estado_civil == "Casado":
        conjugue = st.text_input("Nome do Cônjuge")
        tem_filhos = st.radio("Tem filhos?", ("Sim", "Não"))
        
        if tem_filhos == "Sim":
            num_filhos = st.number_input("Quantos filhos?", min_value=1, step=1)
            for i in range(int(num_filhos)):
                nome_filho = st.text_input(f"Nome do Filho {i+1}")
                idade_filho = st.number_input(f"Idade do Filho {i+1}", min_value=0, step=1)
                filhos.append({"Nome": nome_filho, "Idade": idade_filho})

    # Dados Ministeriais
    st.subheader("Dados Ministeriais")
    consagrado = st.radio("Consagrado?", ("Sim", "Não"))
    local_consagracao = ""
    data_consagracao = None
    
    if consagrado == "Sim":
        local_consagracao = st.text_input("Local da Consagração")
        data_consagracao = st.date_input("Data da Consagração")

    cursou_teologia = st.radio("Cursou Teologia?", ("Sim", "Não"))
    grau_teologia = ""
    
    if cursou_teologia == "Sim":
        grau_teologia = st.selectbox("Grau de Teologia", ["Técnico", "Superior", "Não Cursou"])

    observacoes = st.text_area("Observações")
    cargo = st.selectbox("Cargo", ["Nenhum", "Pastor", "Presbítero", "Diácono", "Obreiro"])
    
    # Interesse em trabalhar na igreja
    st.subheader("Interesse em Trabalhar na Igreja")
    interesse_trabalhar = st.radio("Tem interesse em trabalhar na igreja?", ("Sim", "Não"))
    cargo_interesse = ""
    
    if interesse_trabalhar == "Sim":
        cargo_interesse = st.text_input("Qual o cargo de interesse?")

    # Processa os dados do formulário ao clicar no botão
    if st.button("Enviar"):
        filhos_nomes = [filho['Nome'] for filho in filhos]
        filhos_idades = [filho['Idade'] for filho in filhos]

        # Criação do DataFrame
        df = pd.DataFrame({
            "Nome": [nome],
            "Data de Nascimento": [data_nascimento],
            "Estado Civil": [estado_civil],
            "Profissão": [profissao],
            "Endereço": [endereco],
            "Telefone": [telefone],
            "WhatsApp": [whatsapp],
            "Data que Chegou na Igreja": [data_chegada],
            "Nome do Cônjuge": [conjugue],
            "Filhos (Nomes)": [", ".join(filhos_nomes)],
            "Filhos (Idades)": [", ".join(map(str, filhos_idades))],
            "Consagrado": [consagrado],
            "Local da Consagração": [local_consagracao],
            "Data da Consagração": [data_consagracao],
            "Cursou Teologia": [cursou_teologia],
            "Grau de Teologia": [grau_teologia],
            "Observações": [observacoes],
            "Cargo": [cargo],
            "Interesse em Trabalhar na Igreja": [interesse_trabalhar],
            "Cargo de Interesse": [cargo_interesse]
        })

        # Gera o arquivo Excel em memória
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        # Salva os dados no banco de dados
        cursor.execute('''
          INSERT INTO membros (nome, data_nascimento, estado_civil, conjugue, filhos, consagrado, local_consagracao, data_consagracao, cargo, profissao, endereco, telefone, whatsapp, data_chegada, cursou_teologia, grau_teologia, observacoes)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (nome, data_nascimento, estado_civil, conjugue, str(filhos), consagrado, local_consagracao, data_consagracao, cargo, profissao, endereco, telefone, whatsapp, data_chegada, cursou_teologia, grau_teologia, observacoes))
        conn.commit()

        # Botão para baixar o arquivo Excel
        st.download_button(
            label="Download Excel",
            data=excel_buffer,
            file_name="membros.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Mostrar os últimos 100 dados inseridos
st.subheader("Últimos dados inseridos")
cursor.execute('SELECT * FROM membros ORDER BY id DESC LIMIT 100;')
resultados = cursor.fetchall()
for resultado in resultados:
    st.write(resultado)

# Busca no banco de dados
st.subheader("Busca no banco de dados")
busca = st.text_input("Digite o nome ou parte do nome do membro")
if busca:
    cursor.execute('SELECT * FROM membros WHERE nome LIKE ?;', ('%' + busca + '%',))
    resultados = cursor.fetchall()
    for resultado in resultados:
        st.write(resultado)

# Rodapé com o endereço da igreja e link para o GitHub
st.markdown(
    """
    <footer class="footer">
        <p>&copy; 2024 IGREJA EVANGÉLICA ASSEMBLEIA DE DEUS - MINISTÉRIO FIDELIDADE</p>
        <p>"Nós do ministério Fidelidade sob a proteção de Deus, estamos compromissados na divulgação do evangelho de Jesus Cristo e com a defesa da família".</p>
        <pre>Rua Ernesta Pelosine, 196 - Centro de São Bernardo do Campo - SP</pre>
        <pre>Cep:09771-220 - Tel:(11)2758-2589 - 9.5269-3719</pre>
        
    </footer>
    """,
    unsafe_allow_html=True
)

# Fechar a conexão com o banco de dados
conn.close()
