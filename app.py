import streamlit as st
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Mapeamento das abreviações para os nomes completos dos livros
livros_nomes = {
    "gn": "Gênesis", "ex": "Êxodo", "lv": "Levítico", "nm": "Números", "dt": "Deuteronômio",
    "js": "Josué", "jz": "Juízes", "rt": "Rute", "1sm": "1 Samuel", "2sm": "2 Samuel",
    "1rs": "1 Reis", "2rs": "2 Reis", "1cr": "1 Crônicas", "2cr": "2 Crônicas",
    "ed": "Esdras", "ne": "Neemias", "et": "Ester", "jó": "Jó", "sl": "Salmos",
    "pv": "Provérbios", "ec": "Eclesiastes", "ct": "Cantares", "is": "Isaías",
    "jr": "Jeremias", "lm": "Lamentações", "ez": "Ezequiel", "dn": "Daniel",
    "os": "Oséias", "jl": "Joel", "am": "Amós", "ob": "Obadias", "jn": "Jonas",
    "mq": "Miquéias", "na": "Naum", "hc": "Habacuque", "sf": "Sofonias", "ag": "Ageu",
    "zc": "Zacarias", "ml": "Malaquias", "mt": "Mateus", "mc": "Marcos", "lc": "Lucas",
    "jo": "João", "atos": "Atos", "rm": "Romanos", "1co": "1 Coríntios", "2co": "2 Coríntios",
    "gl": "Gálatas", "ef": "Efésios", "fp": "Filipenses", "cl": "Colossenses",
    "1ts": "1 Tessalonicenses", "2ts": "2 Tessalonicenses", "1tm": "1 Timóteo",
    "2tm": "2 Timóteo", "tt": "Tito", "fm": "Filemom", "hb": "Hebreus",
    "tg": "Tiago", "1pe": "1 Pedro", "2pe": "2 Pedro", "1jo": "1 João",
    "2jo": "2 João", "3jo": "3 João", "jd": "Judas", "ap": "Apocalipse"
}

# Lista de stop words para remover palavras irrelevantes
stop_words = set(["a", "o", "e", "que", "de", "do", "da", "dos", "das",
                  "em", "para", "por", "com", "não", "uma", "como", "se",
                  "mas", "ou", "ao", "às", "os", "as", "isso", "este",
                  "ele", "ela", "eles", "elas", "porque", "porém", "sua", "suas", "seu", "seus", "deu", "lhe", "um", "é", "são", "tu","se", "meu", "nos", "todos", "aos", "na", "deu", "se", "à", "lo", "lhe", "deu", "até", "foi"])

# Função para carregar o JSON da Bíblia
@st.cache_data
def load_biblia():
    with open('nvi.json', 'r', encoding='utf-8-sig') as file:
        return json.load(file)

# Função para contar palavras e remover stop words
def contar_palavras(texto):
    palavras = texto.split()
    return [palavra.lower() for palavra in palavras if palavra.lower() not in stop_words]

# Carregar os dados da Bíblia
biblia_data = load_biblia()

# Criar interface no Streamlit
st.title("📖 Explorador da Bíblia NVI")

# Selecionar livro (mostrando o nome completo)
livros_abrevs = [livro["abbrev"] for livro in biblia_data]
livro_escolhido_abrev = st.selectbox("Escolha um livro:", livros_abrevs, format_func=lambda x: livros_nomes.get(x, x))

# Encontrar os dados do livro escolhido
livro_data = next(livro for livro in biblia_data if livro["abbrev"] == livro_escolhido_abrev)

# Selecionar capítulo
capitulos = list(range(1, len(livro_data["chapters"]) + 1))
capitulo_escolhido = st.selectbox("Escolha um capítulo:", capitulos)

# Selecionar versículo (adicionando opção "Todos")
versiculos = ["Todos"] + list(range(1, len(livro_data["chapters"][capitulo_escolhido - 1]) + 1))
versiculo_escolhido = st.selectbox("Escolha um versículo:", versiculos, index=0)  # Começa sempre com "Todos"

# Exibir o versículo ou todos os versículos
st.write(f"### {livros_nomes[livro_escolhido_abrev]} {capitulo_escolhido}")
if versiculo_escolhido == "Todos":
    for i, versiculo in enumerate(livro_data["chapters"][capitulo_escolhido - 1], start=1):
        st.write(f"*{i}* {versiculo}")
else:
    st.write(f"*{versiculo_escolhido}* {livro_data['chapters'][capitulo_escolhido - 1][versiculo_escolhido - 1]}")

# Criar nuvem de palavras do capítulo selecionado
texto_capitulo = " ".join([palavra for versiculo in livro_data["chapters"][capitulo_escolhido - 1] for palavra in contar_palavras(versiculo)])
wordcloud_capitulo = WordCloud(width=800, height=400, background_color='white').generate(texto_capitulo)

# Criar nuvem de palavras do livro inteiro
texto_livro = " ".join([palavra for cap in livro_data["chapters"] for versiculo in cap for palavra in contar_palavras(versiculo)])
wordcloud_livro = WordCloud(width=800, height=400, background_color='white').generate(texto_livro)

# Exibir nuvem de palavras do capítulo
st.write(f"### Nuvem de palavras do capítulo {capitulo_escolhido} de {livros_nomes[livro_escolhido_abrev]}")
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud_capitulo, interpolation="bilinear")
plt.axis("off")
st.pyplot(plt)

# Exibir nuvem de palavras do livro inteiro
st.write(f"### Nuvem de palavras do livro de {livros_nomes[livro_escolhido_abrev]}")
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud_livro, interpolation="bilinear")
plt.axis("off")
st.pyplot(plt)