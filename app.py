import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import string

# Ensure NLTK stopwords are downloaded
nltk.download('stopwords')
stop_words = set(stopwords.words('portuguese'))  # Adjust for language

# Load the Bible JSON file
@st.cache_data
def load_biblia():
    with open("nvi.json", "r", encoding="utf-8-sig") as file:
        return json.load(file)

biblia_data = load_biblia()

# Mapping abbreviations to full book names
book_names = {
    "gn": "Gênesis", "ex": "Êxodo", "lv": "Levítico", "nm": "Números", "dt": "Deuteronômio",
    "js": "Josué", "jd": "Juízes", "rt": "Rute", "1sm": "1 Samuel", "2sm": "2 Samuel",
    "1rs": "1 Reis", "2rs": "2 Reis", "1cr": "1 Crônicas", "2cr": "2 Crônicas", "ed": "Esdras",
    "ne": "Neemias", "et": "Ester", "jó": "Jó", "sl": "Salmos", "pv": "Provérbios",
    "ec": "Eclesiastes", "ct": "Cantares", "is": "Isaías", "jr": "Jeremias", "lm": "Lamentações",
    "ez": "Ezequiel", "dn": "Daniel", "os": "Oseias", "jl": "Joel", "am": "Amós",
    "ob": "Obadias", "jn": "Jonas", "mq": "Miqueias", "na": "Naum", "hc": "Habacuque",
    "sf": "Sofonias", "ag": "Ageu", "zc": "Zacarias", "ml": "Malaquias",
    "mt": "Mateus", "mc": "Marcos", "lc": "Lucas", "jo": "João",
    "atos": "Atos", "rm": "Romanos", "1co": "1 Coríntios", "2co": "2 Coríntios",
    "gl": "Gálatas", "ef": "Efésios", "fp": "Filipenses", "cl": "Colossenses",
    "1ts": "1 Tessalonicenses", "2ts": "2 Tessalonicenses", "1tm": "1 Timóteo", "2tm": "2 Timóteo",
    "tt": "Tito", "fm": "Filemom", "hb": "Hebreus", "tg": "Tiago", "1pe": "1 Pedro",
    "2pe": "2 Pedro", "1jo": "1 João", "2jo": "2 João", "3jo": "3 João", "jd": "Judas", "ap": "Apocalipse"
}

# Sidebar: Select Book
book_abbr = st.sidebar.selectbox("Selecione um livro", options=[b["abbrev"] for b in biblia_data], format_func=lambda x: book_names.get(x, x))

# Get book data
selected_book = next(b for b in biblia_data if b["abbrev"] == book_abbr)
book_title = book_names.get(book_abbr, book_abbr)

# Sidebar: Select Chapter
chapter_options = ["Todos"] + [str(i + 1) for i in range(len(selected_book["chapters"]))]
selected_chapter = st.sidebar.selectbox("Selecione um capítulo", chapter_options)

# Sidebar: Select Verse
if selected_chapter == "Todos":
    verse_options = ["Todos"]
else:
    verse_options = ["Todos"] + [str(i + 1) for i in range(len(selected_book["chapters"][int(selected_chapter) - 1]))]

selected_verse = st.sidebar.selectbox("Selecione um versículo", verse_options)

# Extracting text
def get_text(book, chapter, verse):
    if chapter == "Todos":
        return [verse for chap in book["chapters"] for verse in chap]
    elif verse == "Todos":
        return book["chapters"][int(chapter) - 1]
    else:
        return [book["chapters"][int(chapter) - 1][int(verse) - 1]]

text_data = get_text(selected_book, selected_chapter, selected_verse)

# Display Book and Chapter
st.title(f"📖 {book_title}")
if selected_chapter == "Todos":
    st.subheader("Todos os capítulos")
elif selected_verse == "Todos":
    st.subheader(f"Capítulo {selected_chapter}")
else:
    st.subheader(f"Versículo {selected_verse} - Capítulo {selected_chapter}")

# Display verses
for i, verse in enumerate(text_data, 1):
    st.markdown(f"**{i}** {verse}")

# 🔹 WORD CLOUD
st.subheader("☁ Nuvem de palavras")

word_freq = Counter(" ".join(text_data).lower().translate(str.maketrans("", "", string.punctuation)).split())
word_freq = {word: count for word, count in word_freq.items() if word not in stop_words}

wordcloud = WordCloud(width=800, height=400, background_color="white", colormap="Blues", max_words=100).generate_from_frequencies(word_freq)

fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)

# 🔹 WORD FREQUENCY BAR CHART
st.subheader("📊 Palavras mais frequentes")

df_word_freq = pd.DataFrame(word_freq.items(), columns=["Palavra", "Frequência"]).nlargest(10, "Frequência")

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(y=df_word_freq["Palavra"], x=df_word_freq["Frequência"], palette="Blues_r", ax=ax)
ax.set_xlabel("Frequência")
ax.set_ylabel("Palavra")
st.pyplot(fig)

# 🔹 VERSE LENGTH OVER TIME (LINE CHART)
st.subheader("📈 Comprimento dos versículos por capítulo")

verse_lengths = [len(" ".join(chap).split()) for chap in selected_book["chapters"]]
df_verse_lengths = pd.DataFrame({"Capítulo": range(1, len(verse_lengths) + 1), "Palavras": verse_lengths})

fig, ax = plt.subplots(figsize=(8, 5))
sns.lineplot(x="Capítulo", y="Palavras", data=df_verse_lengths, marker="o", ax=ax)
ax.set_ylabel("Total de palavras")
ax.set_xlabel("Capítulo")
st.pyplot(fig)

# 🔹 DISTRIBUTION OF VERSE WORD COUNTS (HISTOGRAM)
st.subheader("⏳ Distribuição do tamanho dos versículos")

all_verses = [len(verse.split()) for chap in selected_book["chapters"] for verse in chap]
fig, ax = plt.subplots(figsize=(8, 5))
sns.histplot(all_verses, bins=15, kde=True, color="blue", ax=ax)
ax.set_xlabel("Número de palavras por versículo")
ax.set_ylabel("Frequência")
st.pyplot(fig)
