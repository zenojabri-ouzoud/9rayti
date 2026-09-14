"""
═══════════════════════════════════════════════════════════════════
   🎓 9rayti - تطبيق المراجعة لتلاميذ الإعدادي بالمغرب
   Powered by Google Gemini 🤖
═══════════════════════════════════════════════════════════════════
🚀 التشغيل : streamlit run app.py
═══════════════════════════════════════════════════════════════════
"""

import os
import io
import time
from PIL import Image
import streamlit as st


# ═══════════════════════════════════════════════════════════════════
# ⚙️ الإعدادات
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
    st.error("❌ مفتاح GEMINI_API_KEY غير موجود !")
    st.info("🔑 احصل على مفتاح مجاني : https://aistudio.google.com/app/apikey")
    st.code("GEMINI_API_KEY=AIzaSy...المفتاح...", language="bash")
    st.info("📝 أنشئ ملف `.env` في جذر المشروع.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)


# ═══════════════════════════════════════════════════════════════════
# 📚 البرومبتات للمواد الثمانية
# ═══════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """
أنت أستاذ متمرس في التعليم الثانوي الإعدادي بالمغرب.
تساعد التلاميذ في السنة الأولى والثانية والثالثة إعدادي.
تجيب دائما :
- بطريقة واضحة وبيداغوجية
- منظمة مع رموز تعبيرية
- ملائمة لمستوى التلميذ
- وفق المقرر الرسمي المغربي
- باللغة المطلوبة
"""

PROMPT_MATH = """
أنت أستاذ **الرياضيات** في الإعدادي بالمغرب.
المستوى : {niveau}
اللغة : {langue}

📚 **التمرين** :
{contenu}

أجب بهذه البنية :

## 1. 📝 إعادة صياغة التمرين
## 2. 📊 المعطيات
## 3. 🎯 المطلوب
## 4. 🧮 الطريقة
## 5. ✏️ الحل خطوة بخطوة
## 6. ✅ الجواب النهائي
## 7. 🔍 التحقق
## 8. 💡 نصيحة
## 9. 📚 الدرس المرتبط

⚠️ استعمل : × ÷ √ ² ³ π ≠ ≤ ≥
"""

PROMPT_PHYSIQUE = """
أنت أستاذ **الفيزياء والكيمياء** في الإعدادي بالمغرب.
المستوى : {niveau}
اللغة : {langue}

📚 **التمرين** :
{contenu}

## 1. 📝 التمرين
## 2. 📊 المعطيات (مع الوحدات)
## 3. 🎯 المقدار المطلوب
## 4. 📐 الصيغة
## 5. ✏️ الحساب خطوة بخطوة
## 6. ✅ النتيجة مع الوحدة
## 7. 🔍 التحقق
## 8. 💡 شرح الظاهرة
## 9. ⚠️ أخطاء يجب تجنبها
## 10. 📚 الدرس المرتبط
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
## 4. 💡 حيلة للحفظ

**الصرف والتحويل :**
## 1. 📝 الوزن الصرفي
## 2. ✏️ التحويل
## 3. ✅ الجواب

**البلاغة :**
## 1. 📝 الصورة البلاغية
## 2. ✏️ الشرح
## 3. ✅ الجواب

**التعبير والإنشاء :**
## 1. 📋 التصميم
## 2. ✍️ الإنشاء
## 3. 💡 المفردات الغنية

**القراءة :**
## 1. 📖 التلخيص
## 2. 🔍 الأجوبة
## 3. 💡 شرح المفردات

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
أنت أستاذ **علوم الحياة والأرض** في الإعدادي بالمغرب.
المستوى : {niveau}
اللغة : {langue}

📚 **التمرين** :
{contenu}

## 1. 📝 التمرين
## 2. 🔬 الملاحظات
## 3. 🎯 الإشكال
## 4. 💡 الفرضيات
## 5. 📊 التحليل
## 6. ✅ الاستنتاج
## 7. 🌍 الربط مع المغرب
## 8. 📚 الدرس المرتبط
## 9. ⚠️ أخطاء شائعة
"""

PROMPT_IJTIMA3IYAT = """
أنت أستاذ **الاجتماعيات** في الإعدادي بالمغرب.
المستوى : {niveau}

📚 **التمرين** :
{contenu}

**التاريخ :**
## 1. 📅 السياق التاريخي
## 2. 👥 الأطراف
## 3. 🔍 الأسباب
## 4. 📊 الأحداث
## 5. ✅ النتائج
## 6. 🇲🇦 الربط مع المغرب

**الجغرافيا :**
## 1. 🌍 الموقع
## 2. 📊 المعطيات
## 3. 🔍 التحليل
## 4. 💡 الخلاصة

**التربية على المواطنة :**
## 1. 📝 المفهوم
## 2. ✏️ الشرح
## 3. 💡 أمثلة مغربية
## 4. ✅ الخلاصة

أجب بالعربية الفصحى.
"""

PROMPT_TARBIA_ISLAMIA = """
أنت أستاذ **التربية الإسلامية** في الإعدادي بالمغرب.
المستوى : {niveau}

📚 **التمرين** :
{contenu}

**القرآن الكريم :**
## 1. 📖 الآيات والسورة
## 2. 📝 المعنى الإجمالي
## 3. 💡 شرح المفردات
## 4. ✅ الأحكام والتوجيهات

**الحديث النبوي :**
## 1. 📖 نص الحديث
## 2. 📝 الراوي والمصدر
## 3. 💡 شرح المفردات
## 4. ✅ المعنى والدلالات

**العقيدة :**
## 1. 📝 المفهوم
## 2. 🔍 الأدلة
## 3. ✅ الشرح
## 4. 💡 التطبيق

**الفقه (المذهب المالكي) :**
## 1. 📝 الحكم الشرعي
## 2. 🔍 الدليل
## 3. ✏️ الشروط والأركان
## 4. ✅ التطبيق العملي

**السيرة النبوية :**
## 1. 📅 الحدث وتاريخه
## 2. 👥 الشخصيات
## 3. 🔍 السياق
## 4. 💡 الدروس والعبر

**الأخلاق والقيم :**
## 1. 📝 الخلق/القيمة
## 2. 🔍 الأدلة
## 3. 💡 التطبيق
## 4. ✅ الفوائد

⚠️ اعتمد على المذهب المالكي (المعتمد في المغرب).
أجب بالعربية الفصحى.
"""

PROMPT_COURS = """
أنت أستاذ **{matiere}** في الإعدادي بالمغرب.
المستوى : {niveau}
اللغة : {langue}

📚 **الدرس المطلوب** : {nom_cours}

## 1. 📖 تعريف مبسط
## 2. 📐 الصيغ / القواعد المهمة
## 3. 💡 أمثلة ملموسة (2-3)
## 4. 🎯 منهجية الحل
## 5. ⚠️ أخطاء شائعة
## 6. 🎯 تمارين تطبيقية (مع الحلول)
## 7. 📝 ملخص للحفظ
## 8. 🔗 روابط مع دروس أخرى
## 9. 🇲🇦 مثال من المقرر المغربي
"""


# ═══════════════════════════════════════════════════════════════════
# 📋 القواميس
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
    "📐 الرياضيات": "math",
    "⚗️ الفيزياء والكيمياء": "physique",
    "🌍 اللغة الفرنسية": "francais",
    "🕌 اللغة العربية": "arabe",
    "🇬🇧 اللغة الإنجليزية": "anglais",
    "📖 علوم الحياة والأرض": "svt",
    "🏛️ الاجتماعيات": "ijtima3iyat",
    "☪️ التربية الإسلامية": "tarbia",
}

NOMS_MATIERES = {
    "math": "الرياضيات",
    "physique": "الفيزياء والكيمياء",
    "francais": "اللغة الفرنسية",
    "arabe": "اللغة العربية",
    "anglais": "اللغة الإنجليزية",
    "svt": "علوم الحياة والأرض",
    "ijtima3iyat": "الاجتماعيات",
    "tarbia": "التربية الإسلامية",
}

NIVEAUX = {
    "السنة الأولى إعدادي": "1ere_college",
    "السنة الثانية إعدادي": "2eme_college",
    "السنة الثالثة إعدادي": "3eme_college",
}

LANGUES = {
    "🇲🇦 العربية": "ar",
    "🇫🇷 Français": "fr",
    "🇬🇧 English": "en",
}


# ═══════════════════════════════════════════════════════════════════
# 🤖 خدمة Gemini
# ═══════════════════════════════════════════════════════════════════

def get_generation_config():
    return types.GenerateContentConfig(
        temperature=0.3,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        system_instruction=SYSTEM_PROMPT
    )


def preparer_parts(prompt_texte, image=None, pdf_bytes=None):
    parts = [types.Part.from_text(text=prompt_texte)]

    if image is not None:
        buf = io.BytesIO()
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
    prompt = PROMPTS_MATIERES[matiere].format(
        niveau=niveau,
        langue=langue,
        contenu=texte or "[انظر المرفق]"
    )
    parts = preparer_parts(prompt, image, pdf_bytes)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=parts,
        config=get_generation_config()
    )
    return response.text


def resoudre_multi_exercices(matiere, niveau, langue, exercices):
    nom_matiere = NOMS_MATIERES[matiere]
    intro = f"""
أنت أستاذ {nom_matiere} في الإعدادي بالمغرب.
المستوى : {niveau}
اللغة : {langue}

حل {len(exercices)} تمارين بشكل منفصل.
لكل تمرين، أعط الحل الكامل والمفصل.
"""
    parts = [types.Part.from_text(text=intro)]

    for i, ex in enumerate(exercices, 1):
        parts.append(types.Part.from_text(
            text=f"\n\n═══════════════════════════════\n📝 التمرين رقم {i}\n═══════════════════════════════\n"
        ))
        if ex.get("texte"):
            parts.append(types.Part.from_text(text=ex["texte"]))
        if ex.get("image") is not None:
            buf = io.BytesIO()
            ex["image"].save(buf, format="PNG")
            parts.append(
                types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")
            )

    parts.append(types.Part.from_text(
        text="\n\nافصل الحلول بـ :\n═══ حل التمرين رقم X ═══"
    ))

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=parts,
        config=get_generation_config()
    )
    return response.text


def expliquer_cours(nom_cours, matiere, niveau, langue):
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
    contexte = f"أنت أستاذ {NOMS_MATIERES[matiere]} في الإعدادي بالمغرب."
    prompt = f"{contexte}\n\n❓ السؤال : {question}"
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[types.Part.from_text(text=prompt)],
        config=get_generation_config()
    )
    return response.text


# ═══════════════════════════════════════════════════════════════════
# 🎨 التنسيق
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
# 🏠 العنوان
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div class="main-header">
    <h1>🎓 9rayti</h1>
    <p>أستاذك الخاص الذكي - Powered by Google Gemini 🤖</p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 📊 الشريط الجانبي
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("⚙️ الإعدادات")
    st.markdown("---")

    matiere_label = st.selectbox(
        "📚 المادة",
        options=list(MATIERES.keys()),
        index=0
    )
    matiere = MATIERES[matiere_label]

    niveau_label = st.selectbox(
        "🎯 المستوى",
        options=list(NIVEAUX.keys()),
        index=2
    )
    niveau = NIVEAUX[niveau_label]

    langue_label = st.selectbox(
        "🌍 لغة الجواب",
        options=list(LANGUES.keys()),
        index=0
    )
    langue = LANGUES[langue_label]

    st.markdown("---")
    st.markdown("### 📊 إحصائيات")
    st.metric("المواد", "8")
    st.metric("المستويات", "3")
    st.caption(f"🤖 النموذج : {MODEL_NAME}")


# ═══════════════════════════════════════════════════════════════════
# 🎯 التبويبات
# ═══════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "✏️ حل تمرين",
    "📚📚 تمارين متعددة",
    "📖 شرح درس",
    "💬 طرح سؤال"
])


# ─────────────────────────────────────────────────────────────────
# التبويب 1 : حل تمرين
# ─────────────────────────────────────────────────────────────────

with tab1:
    st.header(f"✏️ حل تمرين — {matiere_label}")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📥 المدخل")

        mode = st.radio(
            "كيف تريد إدخال التمرين ؟",
            ["📷 صورة", "📄 PDF", "⌨️ نص"],
            horizontal=True,
            key="mode_solve"
        )

        image = None
        pdf_bytes = None
        texte = ""

        if mode == "📷 صورة":
            uploaded_image = st.file_uploader(
                "اختر صورة التمرين",
                type=["jpg", "jpeg", "png", "webp"],
                key="img_single"
            )
            if uploaded_image:
                image = Image.open(uploaded_image)
                st.image(image, caption="📷 التمرين", use_column_width=True)

        elif mode == "📄 PDF":
            uploaded_pdf = st.file_uploader(
                "اختر ملف PDF",
                type=["pdf"],
                key="pdf_single"
            )
            if uploaded_pdf:
                pdf_bytes = uploaded_pdf.read()
                st.success(f"✅ تم تحميل PDF ({len(pdf_bytes) // 1024} KB)")

        else:
            texte = st.text_area(
                "اكتب التمرين هنا",
                height=200,
                placeholder="مثال : حل المعادلة 2x + 5 = 13",
                key="txt_single"
            )

        if mode != "⌨️ نص":
            texte_extra = st.text_area(
                "📝 نص إضافي (اختياري)",
                height=100,
                key="txt_extra"
            )
            if texte_extra:
                texte = texte_extra

        bouton = st.button("🚀 حل التمرين", use_container_width=True, key="btn_solve")

    with col2:
        st.subheader("✅ الحل")

        if bouton:
            if not image and not pdf_bytes and not texte.strip():
                st.warning("⚠️ أضف صورة أو PDF أو نصا !")
            else:
                with st.spinner("🤖 Gemini يفكر..."):
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
                        st.success(f"✅ تم الحل في {temps} ثانية")
                        st.markdown("---")
                        st.markdown(solution)
                        st.download_button(
                            "📥 تحميل الحل",
                            data=solution,
                            file_name=f"solution_{matiere}.md",
                            mime="text/markdown"
                        )
                    except Exception as e:
                        st.error(f"❌ خطأ : {str(e)}")
        else:
            st.info("👈 أعد الإعداد ثم اضغط على حل التمرين")


# ─────────────────────────────────────────────────────────────────
# التبويب 2 : تمارين متعددة
# ─────────────────────────────────────────────────────────────────

with tab2:
    st.header(f"📚📚 تمارين متعددة — {matiere_label}")
    st.info("💡 أضف حتى 10 تمارين")

    nb_exercices = st.number_input(
        "عدد التمارين",
        min_value=1,
        max_value=10,
        value=2,
        key="nb_multi"
    )

    exercices = []

    for i in range(int(nb_exercices)):
        with st.expander(f"📝 التمرين رقم {i+1}", expanded=(i == 0)):
            col1, col2 = st.columns(2)

            with col1:
                img_file = st.file_uploader(
                    f"📷 صورة {i+1}",
                    type=["jpg", "jpeg", "png"],
                    key=f"img_multi_{i}"
                )

            with col2:
                txt = st.text_area(
                    f"⌨️ نص {i+1}",
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

    if st.button("🚀 حل جميع التمارين", use_container_width=True, key="btn_multi"):
        if not exercices:
            st.warning("⚠️ أضف تمرينا على الأقل !")
        else:
            with st.spinner(f"🤖 جارٍ حل {len(exercices)} تمارين..."):
                debut = time.time()
                try:
                    solution = resoudre_multi_exercices(
                        matiere=matiere,
                        niveau=niveau,
                        langue=langue,
                        exercices=exercices
                    )
                    temps = round(time.time() - debut, 2)
                    st.success(f"✅ تم حل {len(exercices)} تمارين في {temps} ثانية")
                    st.markdown("---")
                    st.markdown(solution)
                    st.download_button(
                        "📥 تحميل الحلول",
                        data=solution,
                        file_name=f"solutions_{matiere}.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"❌ خطأ : {str(e)}")


# ─────────────────────────────────────────────────────────────────
# التبويب 3 : شرح درس
# ─────────────────────────────────────────────────────────────────

with tab3:
    st.header(f"📖 شرح درس — {matiere_label}")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📝 اسم الدرس")

        nom_cours = st.text_input(
            "أدخل اسم الدرس",
            placeholder="مثال : نظرية فيثاغورس",
            key="nom_cours"
        )

        st.markdown("**💡 اقتراحات :**")
        suggestions = {
            "math": ["نظرية فيثاغورس", "نظرية طاليس", "معادلات الدرجة الأولى"],
            "physique": ["قانون أوم", "الوزن والكتلة", "السرعة"],
            "francais": ["Le passé composé", "Les figures de style"],
            "arabe": ["المبتدأ والخبر", "الفعل الماضي"],
            "anglais": ["Present Simple", "Past Continuous"],
            "svt": ["الهضم", "التركيب الضوئي"],
            "ijtima3iyat": ["الحرب العالمية الأولى", "السكان في المغرب"],
            "tarbia": ["أركان الإسلام", "سورة الفاتحة"],
        }

        for s in suggestions.get(matiere, []):
            if st.button(f"📌 {s}", key=f"sug_{s}"):
                nom_cours = s

        bouton_cours = st.button("📖 شرح الدرس", use_container_width=True, key="btn_cours")

    with col2:
        st.subheader("📚 الشرح")

        if bouton_cours:
            if not nom_cours.strip():
                st.warning("⚠️ أدخل اسم الدرس !")
            else:
                with st.spinner("🤖 جارٍ تحضير الدرس..."):
                    debut = time.time()
                    try:
                        explication = expliquer_cours(
                            nom_cours=nom_cours,
                            matiere=matiere,
                            niveau=niveau,
                            langue=langue
                        )
                        temps = round(time.time() - debut, 2)
                        st.success(f"✅ الدرس جاهز في {temps} ثانية")
                        st.markdown("---")
                        st.markdown(explication)
                        st.download_button(
                            "📥 تحميل الدرس",
                            data=explication,
                            file_name=f"cours_{nom_cours}.md",
                            mime="text/markdown"
                        )
                    except Exception as e:
                        st.error(f"❌ خطأ : {str(e)}")
        else:
            st.info("👈 أدخل اسم الدرس")


# ─────────────────────────────────────────────────────────────────
# التبويب 4 : طرح سؤال
# ─────────────────────────────────────────────────────────────────

with tab4:
    st.header("💬 طرح سؤال")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    col_a, col_b = st.columns([4, 1])
    with col_b:
        if st.button("🗑️ مسح", key="btn_reset"):
            st.session_state.messages = []
            st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("اطرح سؤالك...")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("🤖 Gemini يفكر..."):
                try:
                    reponse = poser_question(question, matiere)
                    st.markdown(reponse)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": reponse}
                    )
                except Exception as e:
                    st.error(f"❌ خطأ : {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# 📄 التذييل
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888;'>"
    "🎓 <b>9rayti</b> — Powered by Google Gemini 🤖 | Made with ❤️ in Morocco 🇲🇦"
    "</div>",
    unsafe_allow_html=True
)
