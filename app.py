import streamlit as st
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud
from collections import Counter
import io
from bs4 import BeautifulSoup  # Adicionado para remover tags HTML

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
                  "ele", "ela", "eles", "elas", "porque", "porém", "sua", "suas",
                  "seu", "seus", "deu", "lhe", "um", "é", "são", "tu","se", "meu",
                  "nos", "todos", "aos", "na", "deu", "se", "à", "lo", "lhe", "deu",
                  "até", "foi", "você", "se", "lhe", "deu", "quem", "então", "os", "as",
                  "um", "com" "se", "no", "sua","seu", "'", "me", "lhes","pois","sem", "está",
                  "vocês", "eu","quando","nem","alguém","—","minha","vocês,", "estão", "senhor,"])


@st.cache_data
def load_biblia():
    with open('nvi.json', 'r', encoding='utf-8-sig') as file:
        return json.load(file)

def contar_palavras(texto):
    palavras = texto.split()
    return [palavra.lower() for palavra in palavras if palavra.lower() not in stop_words]

# Função para remover tags HTML
def remover_tags_html(texto):
    soup = BeautifulSoup(texto, "html.parser")
    return soup.get_text()

# Carregar os dados da Bíblia
biblia_data = load_biblia()

st.title("📖 Explorador da Bíblia NVI")

livros_abrevs = [livro["abbrev"] for livro in biblia_data]
livro_escolhido = st.selectbox("Escolha um livro:", livros_abrevs, format_func=lambda x: livros_nomes.get(x, x))

livro_data = next(livro for livro in biblia_data if livro["abbrev"] == livro_escolhido)
capitulos = ["Todos"] + list(range(1, len(livro_data["chapters"]) + 1))
capitulo_escolhido = st.selectbox("Escolha um capítulo:", capitulos)

if capitulo_escolhido == "Todos":
    versiculos = ["Todos"]
else:
    versiculos = ["Todos"] + list(range(1, len(livro_data["chapters"][capitulo_escolhido - 1]) + 1))
versiculo_escolhido = st.selectbox("Escolha um versículo:", versiculos)

st.write(f"### {livros_nomes[livro_escolhido]}")

# Estruturação do texto
if capitulo_escolhido == "Todos":
    texto_completo = ""
    for cap_num, capitulo in enumerate(livro_data["chapters"], start=1):
        texto_completo += f"<h3>Capítulo {cap_num}</h3>"  # Título do capítulo
        for vers_num, versiculo in enumerate(capitulo, start=1):
            texto_completo += f"<p><strong>{vers_num}</strong> {versiculo}</p>"  # Versículo formatado
        texto_completo += "<hr>"  # Linha horizontal entre capítulos
elif versiculo_escolhido == "Todos":
    texto_completo = ""
    for vers_num, versiculo in enumerate(livro_data["chapters"][capitulo_escolhido - 1], start=1):
        texto_completo += f"<p><strong>{vers_num}</strong> {versiculo}</p>"  # Versículo formatado
else:
    texto_completo = f"<p><strong>{versiculo_escolhido}</strong> {livro_data['chapters'][capitulo_escolhido - 1][versiculo_escolhido - 1]}</p>"

# Exibe o texto formatado com HTML e rolagem
st.markdown(
    f'<div style="height: 400px; overflow-y: auto;">{texto_completo}</div>',
    unsafe_allow_html=True
)

# Limpar o texto antes de gerar a nuvem de palavras
texto_limpo = remover_tags_html(texto_completo)

# Estatísticas
total_palavras_biblia = sum(len(contar_palavras(" ".join(cap))) for livro in biblia_data for cap in livro["chapters"])
palavras_livro = len(contar_palavras(texto_limpo))
percentual = (palavras_livro / total_palavras_biblia) * 100
st.write(f"📊 O livro {livros_nomes[livro_escolhido]} representa {percentual:.2f}% do total de palavras da Bíblia.")

# Gráficos
st.write("### Nuvem de Palavras")
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(contar_palavras(texto_limpo)))
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
st.pyplot(plt)

st.write("### Distribuição de Palavras")
df = pd.DataFrame(Counter(contar_palavras(texto_limpo)).most_common(15), columns=['Palavra', 'Frequência'])
plt.figure(figsize=(8, 5))
sns.barplot(x='Frequência', y='Palavra', data=df, palette='viridis')
st.pyplot(plt)

st.write("### Comprimento dos Versículos")
verso_lengths = [len(contar_palavras(verso)) for cap in livro_data["chapters"] for verso in cap]
plt.figure(figsize=(8, 5))
sns.histplot(verso_lengths, bins=20, kde=True, color='blue')
st.pyplot(plt)

st.write("### Proporção do Livro na Bíblia")
plt.figure(figsize=(6, 6))
plt.pie([palavras_livro, total_palavras_biblia - palavras_livro], labels=[livros_nomes[livro_escolhido], "Resto da Bíblia"], autopct='%1.1f%%', colors=['green', 'gray'])
st.pyplot(plt)

if st.button("Copiar Texto"):
    st.write("Texto copiado para a área de transferência! (Simulação)")