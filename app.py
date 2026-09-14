"""
═══════════════════════════════════════════════════════════════════
   🎓 9rayti - Application de révision pour collégiens marocains
   Powered by Google Gemini (nouvelle API google-genai) 🤖
═══════════════════════════════════════════════════════════════════
🚀 LANCEMENT : streamlit run app.py
═══════════════════════════════════════════════════════════════════
"""

import os
import time
from PIL import Image
import streamlit as st
from dotenv import load_dotenv

# ═══════════════════════════════════════════════════════════════════
# ⚙️ CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="9rayti 🎓",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()


def get_config(key, default=""):
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


GEMINI_API_KEY = get_config("GEMINI_API_KEY")
MODEL_NAME = get_config("MODEL_NAME", "gemini-2.0-flash")

if not GEMINI_API_KEY:
    st.error("❌ Clé GEMINI_API_KEY manquante !")
    st.info("🔑 Obtiens une clé gratuite : https://aistudio.google.com/app/apikey")
    st.code("GEMINI_API_KEY=AIzaSy...ta_clé...", language="bash")
    st.info("📝 Crée un fichier `.env` à la racine du projet.")
    st.stop()

# Nouveau client Gemini
client = genai.Client(api_key=GEMINI_API_KEY)


# ═══════════════════════════════════════════════════════════════════
# 📚 PROMPTS DES 8 MATIÈRES
# ═══════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """
Tu es un professeur expérimenté au collège au Maroc.
Tu aides les élèves de 1ère, 2ème et 3ème année collège.
Tu réponds toujours :
- De manière claire et pédagogique
- Structurée avec des emojis
- Adaptée au niveau de l'élève
- En respectant le programme officiel marocain
- Dans la langue demandée
"""

PROMPT_MATH = """
Tu es un professeur de **Mathématiques** au collège au Maroc.
Niveau : {niveau}
Langue : {langue}

📚 **Exercice** :
{contenu}

Réponds avec cette structure :

## 1. 📝 Énoncé reformulé
## 2. 📊 Données
## 3. 🎯 Ce qu'on cherche
## 4. 🧮 Méthode
## 5. ✏️ Résolution étape par étape
## 6. ✅ Réponse finale
## 7. 🔍 Vérification
## 8. 💡 Conseil
## 9. 📚 Cours lié

⚠️ Utilise : × ÷ √ ² ³ π ≠ ≤ ≥
"""

PROMPT_PHYSIQUE = """
Tu es un professeur de **Physique-Chimie** au collège au Maroc.
Niveau : {niveau}
Langue : {langue}

📚 **Exercice** :
{contenu}

## 1. 📝 Énoncé
## 2. 📊 Données (avec UNITÉS)
## 3. 🎯 Grandeur cherchée
## 4. 📐 Formule
## 5. ✏️ Calcul étape par étape
## 6. ✅ Résultat avec unité
## 7. 🔍 Vérification
## 8. 💡 Explication
## 9. ⚠️ Pièges à éviter
## 10. 📚 Cours lié
"""

PROMPT_FRANCAIS = """
Tu es un professeur de **Français** au collège au Maroc.
Niveau : {niveau}

📚 **Exercice** :
{contenu}

Selon le type :

**GRAMMAIRE/CONJUGAISON/ORTHOGRAPHE :**
## 1. 📝 Règle
## 2. ✏️ Analyse
## 3. ✅ Réponse
## 4. 💡 Astuce

**COMPRÉHENSION :**
## 1. 📖 Résumé
## 2. 🔍 Réponses
## 3. 📚 Vocabulaire

**EXPRESSION ÉCRITE :**
## 1. 📋 Plan
## 2. ✍️ Rédaction
## 3. 💡 Vocabulaire riche
"""

PROMPT_ARABE = """
أنت أستاذ **اللغة العربية** في الإعدادي بالمغرب.
المستوى : {niveau}

📚 **التمرين** :
{contenu}

**النحو :**
## 1. 📝 القاعدة
## 2. ✏️ الإعراب
## 3. ✅ الجواب
## 4. 💡 حيلة

**الصرف :**
## 1. 📝 الوزن
## 2. ✏️ التحويل
## 3. ✅ الجواب

**البلاغة :**
## 1. 📝 الصورة
## 2. ✏️ الشرح
## 3. ✅ الجواب

**التعبير :**
## 1. 📋 التصميم
## 2. ✍️ الإنشاء
## 3. 💡 المفردات

**القراءة :**
## 1. 📖 التلخيص
## 2. 🔍 الأجوبة
## 3. 💡 المفردات

أجب بالعربية الفصحى.
"""

PROMPT_ANGLAIS = """
You are an **English teacher** for middle school in Morocco.
Level : {niveau}
Language : {langue}

📚 **Exercise** :
{contenu}

**GRAMMAR :**
## 1. 📝 Rule
## 2. ✏️ Examples
## 3. ✅ Answer
## 4. 💡 Tip

**VOCABULARY :**
## 1. 📖 Meaning
## 2. ✏️ Translation
## 3. 💡 Usage

**READING :**
## 1. 📖 Summary
## 2. 🔍 Answers
## 3. 📚 Words

**WRITING :**
## 1. 📋 Plan
## 2. ✍️ Writing
## 3. 💡 Expressions
"""

PROMPT_SVT = """
Tu es un professeur de **SVT** au collège au Maroc.
Niveau : {niveau}
Langue : {langue}

📚 **Exercice** :
{contenu}

## 1. 📝 Énoncé
## 2. 🔬 Observations
## 3. 🎯 Problème
## 4. 💡 Hypothèses
## 5. 📊 Analyse
## 6. ✅ Conclusion
## 7. 🌍 Lien avec le Maroc
## 8. 📚 Cours lié
## 9. ⚠️ Erreurs fréquentes
"""

PROMPT_IJTIMA3IYAT = """
أنت أستاذ **الاجتماعيات** في الإعدادي بالمغرب.
المستوى : {niveau}

📚 **التمرين** :
{contenu}

**التاريخ :**
## 1. 📅 السياق
## 2. 👥 الأطراف
## 3. 🔍 الأسباب
## 4. 📊 الأحداث
## 5. ✅ النتائج
## 6. 🇲🇦 الرابط مع المغرب

**الجغرافيا :**
## 1. 🌍 الموقع
## 2. 📊 المعطيات
## 3. 🔍 التحليل
## 4. 💡 الخلاصة

**المواطنة :**
## 1. 📝 المفهوم
## 2. ✏️ الشرح
## 3. 💡 أمثلة
## 4. ✅ الخلاصة

أجب بالعربية الفصحى.
"""

PROMPT_TARBIA_ISLAMIA = """
أنت أستاذ **التربية الإسلامية** في الإعدادي بالمغرب.
المستوى : {niveau}

📚 **التمرين** :
{contenu}

**القرآن :**
## 1. 📖 الآيات
## 2. 📝 المعنى
## 3. 💡 المفردات
## 4. ✅ الأحكام

**الحديث :**
## 1. 📖 النص
## 2. 📝 الراوي
## 3. 💡 الشرح
## 4. ✅ الدلالات

**العقيدة :**
## 1. 📝 المفهوم
## 2. 🔍 الأدلة
## 3. ✅ الشرح
## 4. 💡 التطبيق

**الفقه (مالكي) :**
## 1. 📝 الحكم
## 2. 🔍 الدليل
## 3. ✏️ الشروط
## 4. ✅ التطبيق

**السيرة :**
## 1. 📅 الحدث
## 2. 👥 الشخصيات
## 3. 🔍 السياق
## 4. 💡 الدروس

**الأخلاق :**
## 1. 📝 الخلق
## 2. 🔍 الأدلة
## 3. 💡 التطبيق
## 4. ✅ الفوائد

⚠️ اعتمد على المذهب المالكي.
أجب بالعربية الفصحى.
"""

PROMPT_COURS = """
Tu es un professeur de **{matiere}** au collège au Maroc.
Niveau : {niveau}
Langue : {langue}

📚 **Cours** : {nom_cours}

## 1. 📖 Définition simple
## 2. 📐 Formules / Règles
## 3. 💡 Exemples (2-3)
## 4. 🎯 Méthode de résolution
## 5. ⚠️ Erreurs fréquentes
## 6. 🎯 Exercices d'application
## 7. 📝 Fiche mémo
## 8. 🔗 Liens avec d'autres cours
## 9. 🇲🇦 Exemple marocain
"""


# ═══════════════════════════════════════════════════════════════════
# 📋 DICTIONNAIRES
# ═══════════════════════════════════════════════════════════════════

PROMPTS_MATIERES = {
    "math": PROMPT_MATH,
    "physique": PROMPT_PHYSIQUE,
    "francais": PROMPT_FRANCAIS,
    "arabe": PROMPT_ARABE,
    "anglais": PROMPT_ANGLAIS,
    "svt": PROMPT_SVT,
    "ijtima3iyat": PROMPT_IJTIMA3IYAT,
    "tarbia": PROMPT_TARBIA_ISLAMIA,
}

MATIERES = {
    "📐 Mathématiques": "math",
    "⚗️ Physique-Chimie": "physique",
    "🌍 Français": "francais",
    "🕌 Arabe": "arabe",
    "🇬🇧 Anglais": "anglais",
    "📖 SVT": "svt",
    "🏛️ Histoire-Géo": "ijtima3iyat",
    "☪️ Éducation Islamique": "tarbia",
}

NOMS_MATIERES = {
    "math": "Mathématiques",
    "physique": "Physique-Chimie",
    "francais": "Français",
    "arabe": "Arabe",
    "anglais": "Anglais",
    "svt": "SVT",
    "ijtima3iyat": "Histoire-Géo",
    "tarbia": "Éducation Islamique",
}

NIVEAUX = {
    "1ère année collège": "1ere_college",
    "2ème année collège": "2eme_college",
    "3ème année collège": "3eme_college",
}

LANGUES = {
    "🇫🇷 Français": "fr",
    "🇲🇦 العربية": "ar",
    "🇬🇧 English": "en",
}


# ═══════════════════════════════════════════════════════════════════
# 🤖 SERVICE GEMINI (nouvelle API)
# ═══════════════════════════════════════════════════════════════════

def get_generation_config():
    """Config de génération pour Gemini"""
    return types.GenerateContentConfig(
        temperature=0.3,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        system_instruction=SYSTEM_PROMPT
    )


def preparer_parts(prompt_texte, image=None, pdf_bytes=None):
    """Préparer les 'parts' du contenu multimodal"""
    parts = [types.Part.from_text(text=prompt_texte)]

    if image is not None:
        # Convertir PIL Image en bytes PNG
        import io as _io
        buf = _io.BytesIO()
        image.save(buf, format="PNG")
        parts.append(
            types.Part.from_bytes(
                data=buf.getvalue(),
                mime_type="image/png"
            )
        )
    elif pdf_bytes is not None:
        parts.append(
            types.Part.from_bytes(
                data=pdf_bytes,
                mime_type="application/pdf"
            )
        )
    return parts


def resoudre_exercice(matiere, niveau, langue, texte, image=None, pdf_bytes=None):
    """Résoudre un exercice"""
    prompt = PROMPTS_MATIERES[matiere].format(
        niveau=niveau,
        langue=langue,
        contenu=texte or "[Voir pièce jointe]"
    )
    parts = preparer_parts(prompt, image, pdf_bytes)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=parts,
        config=get_generation_config()
    )
    return response.text


def resoudre_multi_exercices(matiere, niveau, langue, exercices):
    """Résoudre plusieurs exercices"""
    nom_matiere = NOMS_MATIERES[matiere]
    intro = f"""
Tu es un professeur de {nom_matiere} au collège au Maroc.
Niveau : {niveau}
Langue : {langue}

Résous {len(exercices)} exercices SÉPARÉMENT.
Pour CHAQUE exercice, donne une solution complète.
"""
    parts = [types.Part.from_text(text=intro)]

    for i, ex in enumerate(exercices, 1):
        parts.append(types.Part.from_text(
            text=f"\n\n═══════════════════════════════\n📝 EXERCICE N°{i}\n═══════════════════════════════\n"
        ))
        if ex.get("texte"):
            parts.append(types.Part.from_text(text=ex["texte"]))
        if ex.get("image") is not None:
            import io as _io
            buf = _io.BytesIO()
            ex["image"].save(buf, format="PNG")
            parts.append(
                types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")
            )

    parts.append(types.Part.from_text(
        text="\n\nSépare les solutions par :\n═══ SOLUTION EXERCICE N°X ═══"
    ))

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=parts,
        config=get_generation_config()
    )
    return response.text


def expliquer_cours(nom_cours, matiere, niveau, langue):
    """Expliquer un cours détaillé"""
    nom_matiere = NOMS_MATIERES.get(matiere, matiere)
    prompt = PROMPT_COURS.format(
        matiere=nom_matiere,
        niveau=niveau,
        langue=langue,
        nom_cours=nom_cours
    )
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[types.Part.from_text(text=prompt)],
        config=get_generation_config()
    )
    return response.text


def poser_question(question, matiere):
    """Question libre"""
    contexte = f"Tu es un professeur de {NOMS_MATIERES[matiere]} au collège au Maroc."
    prompt = f"{contexte}\n\n❓ Question : {question}"
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[types.Part.from_text(text=prompt)],
        config=get_generation_config()
    )
    return response.text


# ═══════════════════════════════════════════════════════════════════
# 🎨 CSS
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #006233 0%, #C1272D 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: #f0f0f0;
        margin-top: 0.5rem;
        font-size: 1.1rem;
    }
    .stButton>button {
        background: #006233;
        color: white;
        border-radius: 10px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background: #C1272D;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 🏠 HEADER
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div class="main-header">
    <h1>🎓 9rayti</h1>
    <p>Ton professeur particulier intelligent - Powered by Google Gemini 🤖</p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 📊 SIDEBAR
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")

    matiere_label = st.selectbox(
        "📚 Matière",
        options=list(MATIERES.keys()),
        index=0
    )
    matiere = MATIERES[matiere_label]

    niveau_label = st.selectbox(
        "🎯 Niveau",
        options=list(NIVEAUX.keys()),
        index=2
    )
    niveau = NIVEAUX[niveau_label]

    langue_label = st.selectbox(
        "🌍 Langue de réponse",
        options=list(LANGUES.keys()),
        index=0
    )
    langue = LANGUES[langue_label]

    st.markdown("---")
    st.markdown("### 📊 Stats")
    st.metric("Matières", "8")
    st.metric("Niveaux", "3")
    st.caption(f"🤖 Modèle : {MODEL_NAME}")


# ═══════════════════════════════════════════════════════════════════
# 🎯 ONGLETS
# ═══════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "✏️ Résoudre un exercice",
    "📚📚 Multi-exercices",
    "📖 Expliquer un cours",
    "💬 Poser une question"
])


# ─────────────────────────────────────────────────────────────────
# ONGLET 1 : RÉSOUDRE UN EXERCICE
# ─────────────────────────────────────────────────────────────────

with tab1:
    st.header(f"✏️ Résoudre un exercice — {matiere_label}")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📥 Entrée")

        mode = st.radio(
            "Comment veux-tu donner l'exercice ?",
            ["📷 Photo", "📄 PDF", "⌨️ Texte"],
            horizontal=True,
            key="mode_solve"
        )

        image = None
        pdf_bytes = None
        texte = ""

        if mode == "📷 Photo":
            uploaded_image = st.file_uploader(
                "Choisis une photo",
                type=["jpg", "jpeg", "png", "webp"],
                key="img_single"
            )
            if uploaded_image:
                image = Image.open(uploaded_image)
                st.image(image, caption="📷 Exercice", use_column_width=True)

        elif mode == "📄 PDF":
            uploaded_pdf = st.file_uploader(
                "Choisis un PDF",
                type=["pdf"],
                key="pdf_single"
            )
            if uploaded_pdf:
                pdf_bytes = uploaded_pdf.read()
                st.success(f"✅ PDF chargé ({len(pdf_bytes) // 1024} KB)")

        else:
            texte = st.text_area(
                "Écris ton exercice",
                height=200,
                placeholder="Exemple : Résoudre 2x + 5 = 13",
                key="txt_single"
            )

        if mode != "⌨️ Texte":
            texte_extra = st.text_area(
                "📝 Texte additionnel (optionnel)",
                height=100,
                key="txt_extra"
            )
            if texte_extra:
                texte = texte_extra

        bouton = st.button("🚀 Résoudre", use_container_width=True, key="btn_solve")

    with col2:
        st.subheader("✅ Solution")

        if bouton:
            if not image and not pdf_bytes and not texte.strip():
                st.warning("⚠️ Ajoute une photo, un PDF ou du texte !")
            else:
                with st.spinner("🤖 Gemini réfléchit..."):
                    debut = time.time()
                    try:
                        solution = resoudre_exercice(
                            matiere=matiere,
                            niveau=niveau,
                            langue=langue,
                            texte=texte,
                            image=image,
                            pdf_bytes=pdf_bytes
                        )
                        temps = round(time.time() - debut, 2)
                        st.success(f"✅ Solution trouvée en {temps}s")
                        st.markdown("---")
                        st.markdown(solution)
                        st.download_button(
                            "📥 Télécharger",
                            data=solution,
                            file_name=f"solution_{matiere}.md",
                            mime="text/markdown"
                        )
                    except Exception as e:
                        st.error(f"❌ Erreur : {str(e)}")
        else:
            st.info("👈 Configure puis clique sur Résoudre")


# ─────────────────────────────────────────────────────────────────
# ONGLET 2 : MULTI-EXERCICES
# ─────────────────────────────────────────────────────────────────

with tab2:
    st.header(f"📚📚 Multi-exercices — {matiere_label}")
    st.info("💡 Ajoute jusqu'à 10 exercices")

    nb_exercices = st.number_input(
        "Nombre d'exercices",
        min_value=1,
        max_value=10,
        value=2,
        key="nb_multi"
    )

    exercices = []

    for i in range(int(nb_exercices)):
        with st.expander(f"📝 Exercice N°{i+1}", expanded=(i == 0)):
            col1, col2 = st.columns(2)

            with col1:
                img_file = st.file_uploader(
                    f"📷 Photo {i+1}",
                    type=["jpg", "jpeg", "png"],
                    key=f"img_multi_{i}"
                )

            with col2:
                txt = st.text_area(
                    f"⌨️ Texte {i+1}",
                    key=f"txt_multi_{i}",
                    height=100
                )

            ex = {}
            if img_file:
                ex["image"] = Image.open(img_file)
            if txt.strip():
                ex["texte"] = txt.strip()

            if ex:
                exercices.append(ex)

    if st.button("🚀 Résoudre tous", use_container_width=True, key="btn_multi"):
        if not exercices:
            st.warning("⚠️ Ajoute au moins un exercice !")
        else:
            with st.spinner(f"🤖 Résolution de {len(exercices)} exercices..."):
                debut = time.time()
                try:
                    solution = resoudre_multi_exercices(
                        matiere=matiere,
                        niveau=niveau,
                        langue=langue,
                        exercices=exercices
                    )
                    temps = round(time.time() - debut, 2)
                    st.success(f"✅ {len(exercices)} exercices résolus en {temps}s")
                    st.markdown("---")
                    st.markdown(solution)
                    st.download_button(
                        "📥 Télécharger",
                        data=solution,
                        file_name=f"solutions_{matiere}.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"❌ Erreur : {str(e)}")


# ─────────────────────────────────────────────────────────────────
# ONGLET 3 : EXPLIQUER UN COURS
# ─────────────────────────────────────────────────────────────────

with tab3:
    st.header(f"📖 Expliquer un cours — {matiere_label}")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📝 Nom du cours")

        nom_cours = st.text_input(
            "Entre le nom du cours",
            placeholder="Ex: Théorème de Pythagore",
            key="nom_cours"
        )

        st.markdown("**💡 Suggestions :**")
        suggestions = {
            "math": ["Théorème de Pythagore", "Théorème de Thalès", "Équations 1er degré"],
            "physique": ["Loi d'Ohm", "Poids et masse", "Vitesse"],
            "francais": ["Le passé composé", "Les figures de style"],
            "arabe": ["المبتدأ والخبر", "الفعل الماضي"],
            "anglais": ["Present Simple", "Past Continuous"],
            "svt": ["La digestion", "La photosynthèse"],
            "ijtima3iyat": ["الحرب العالمية الأولى", "السكان في المغرب"],
            "tarbia": ["أركان الإسلام", "سورة الفاتحة"],
        }

        for s in suggestions.get(matiere, []):
            if st.button(f"📌 {s}", key=f"sug_{s}"):
                nom_cours = s

        bouton_cours = st.button("📖 Expliquer", use_container_width=True, key="btn_cours")

    with col2:
        st.subheader("📚 Explication")

        if bouton_cours:
            if not nom_cours.strip():
                st.warning("⚠️ Entre le nom du cours !")
            else:
                with st.spinner("🤖 Préparation du cours..."):
                    debut = time.time()
                    try:
                        explication = expliquer_cours(
                            nom_cours=nom_cours,
                            matiere=matiere,
                            niveau=niveau,
                            langue=langue
                        )
                        temps = round(time.time() - debut, 2)
                        st.success(f"✅ Cours prêt en {temps}s")
                        st.markdown("---")
                        st.markdown(explication)
                        st.download_button(
                            "📥 Télécharger",
                            data=explication,
                            file_name=f"cours_{nom_cours}.md",
                            mime="text/markdown"
                        )
                    except Exception as e:
                        st.error(f"❌ Erreur : {str(e)}")
        else:
            st.info("👈 Entre le nom du cours")


# ─────────────────────────────────────────────────────────────────
# ONGLET 4 : QUESTION LIBRE
# ─────────────────────────────────────────────────────────────────

with tab4:
    st.header("💬 Poser une question")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    col_a, col_b = st.columns([4, 1])
    with col_b:
        if st.button("🗑️ Effacer", key="btn_reset"):
            st.session_state.messages = []
            st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Pose ta question...")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("🤖 Gemini réfléchit..."):
                try:
                    reponse = poser_question(question, matiere)
                    st.markdown(reponse)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": reponse}
                    )
                except Exception as e:
                    st.error(f"❌ Erreur : {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# 📄 FOOTER
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888;'>"
    "🎓 <b>9rayti</b> — Powered by Google Gemini 🤖 | Made with ❤️ in Morocco 🇲🇦"
    "</div>",
    unsafe_allow_html=True
)
