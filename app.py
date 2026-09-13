"""
═══════════════════════════════════════════════════════════════════
   🎓 RévisoMaroc API - Backend COMPLET en un seul fichier
   Powered by Google Gemini 🤖
   
   8 matières : Math, Physique, Français, Arabe, Anglais, SVT,
                Histoire-Géo, Éducation Islamique
═══════════════════════════════════════════════════════════════════

📦 INSTALLATION :
    pip install fastapi uvicorn python-multipart python-dotenv google-generativeai Pillow aiofiles

🔑 OBTENIR UNE CLÉ GEMINI GRATUITE :
    https://aistudio.google.com/app/apikey

🚀 LANCEMENT :
    python main.py
    
    Puis ouvre : http://localhost:8000/docs
"""

import os
import io
import time
import base64
from typing import Optional, List
from enum import Enum

from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv


# ═══════════════════════════════════════════════════════════════════
# ⚙️ CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

if not GEMINI_API_KEY:
    print("⚠️  ATTENTION : GEMINI_API_KEY manquante dans .env")
    print("🔑 Obtiens une clé gratuite : https://aistudio.google.com/app/apikey")

genai.configure(api_key=GEMINI_API_KEY)


# ═══════════════════════════════════════════════════════════════════
# 📚 PROMPTS POUR LES 8 MATIÈRES
# ═══════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """
Tu es un professeur expérimenté au collège au Maroc.
Tu aides les élèves de 1ère, 2ème et 3ème année collège.
Tu réponds toujours :
- De manière claire et pédagogique
- Structurée avec des emojis
- Adaptée au niveau de l'élève
- En respectant le programme officiel marocain
- Dans la langue demandée (arabe ou français ou anglais)
"""

PROMPT_MATH = """
Tu es un professeur de **Mathématiques** au collège au Maroc.
Niveau : {niveau}
Langue : {langue}

📚 **Exercice** :
{contenu}

Réponds EXACTEMENT avec cette structure :

## 1. 📝 Énoncé reformulé
## 2. 📊 Données
## 3. 🎯 Ce qu'on cherche
## 4. 🧮 Méthode à utiliser
## 5. ✏️ Résolution étape par étape
## 6. ✅ Réponse finale (en gras)
## 7. 🔍 Vérification
## 8. 💡 Conseil / Astuce
## 9. 📚 Cours lié

⚠️ Utilise les symboles : × ÷ √ ² ³ π ≠ ≤ ≥
"""

PROMPT_PHYSIQUE = """
Tu es un professeur de **Physique-Chimie** au collège au Maroc.
Niveau : {niveau}
Langue : {langue}

📚 **Exercice** :
{contenu}

Structure :
## 1. 📝 Énoncé
## 2. 📊 Données (avec UNITÉS)
## 3. 🎯 Grandeur cherchée
## 4. 📐 Formule
## 5. ✏️ Calcul étape par étape
## 6. ✅ Résultat avec unité
## 7. 🔍 Vérification
## 8. 💡 Explication du phénomène
## 9. ⚠️ Pièges à éviter
## 10. 📚 Cours lié

⚠️ N'oublie JAMAIS les unités (m, s, kg, N, J, W, V, A, Ω, °C, mol...)
"""

PROMPT_FRANCAIS = """
Tu es un professeur de **Français** au collège au Maroc.
Niveau : {niveau}

📚 **Exercice** :
{contenu}

Détecte le type et réponds :

**GRAMMAIRE/CONJUGAISON/ORTHOGRAPHE :**
## 1. 📝 Règle
## 2. ✏️ Analyse
## 3. ✅ Réponse
## 4. 💡 Astuce
## 5. ⚠️ Erreurs fréquentes

**COMPRÉHENSION :**
## 1. 📖 Résumé
## 2. 🔍 Réponses
## 3. 📚 Vocabulaire
## 4. 💡 Idée principale

**EXPRESSION ÉCRITE :**
## 1. 📋 Plan
## 2. ✍️ Rédaction complète
## 3. 💡 Vocabulaire riche
## 4. ⚠️ Erreurs à éviter

**LECTURE / POÉSIE :**
## 1. 📖 Analyse
## 2. 🎭 Figures de style
## 3. 💡 Interprétation
"""

PROMPT_ARABE = """
أنت أستاذ **اللغة العربية** في التعليم الثانوي الإعدادي بالمغرب.
المستوى : {niveau}

📚 **التمرين** :
{contenu}

حدد النوع وأجب :

**النحو :**
## 1. 📝 القاعدة
## 2. ✏️ الإعراب الكامل
## 3. ✅ الجواب
## 4. 💡 حيلة للحفظ

**الصرف والتحويل :**
## 1. 📝 الوزن الصرفي
## 2. ✏️ التحويل
## 3. ✅ الجواب

**البلاغة :**
## 1. 📝 الصورة البلاغية
## 2. ✏️ شرحها وسر جمالها
## 3. ✅ الجواب

**التعبير والإنشاء :**
## 1. 📋 تصميم الموضوع
## 2. ✍️ الإنشاء الكامل
## 3. 💡 المفردات الغنية

**القراءة :**
## 1. 📖 تلخيص النص
## 2. 🔍 أجوبة الأسئلة
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
## 4. 💡 Memory tip

**VOCABULARY :**
## 1. 📖 Meaning
## 2. ✏️ Translation
## 3. 💡 Usage in sentences

**READING :**
## 1. 📖 Summary
## 2. 🔍 Answers
## 3. 📚 Difficult words

**WRITING :**
## 1. 📋 Plan
## 2. ✍️ Full writing
## 3. 💡 Useful expressions

**TRANSLATION :**
## 1. 📝 Key words
## 2. ✏️ Translation
## 3. 💡 Grammar notes
"""

PROMPT_SVT = """
Tu es un professeur de **SVT** au collège au Maroc.
Niveau : {niveau}
Langue : {langue}

📚 **Exercice** :
{contenu}

## 1. 📝 Énoncé
## 2. 🔬 Observations / Données
## 3. 🎯 Problème à résoudre
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
## 1. 📅 السياق التاريخي
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
## 5. 🇲🇦 أمثلة مغربية

**المواطنة :**
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

**القرآن :**
## 1. 📖 الآيات والسورة
## 2. 📝 المعنى الإجمالي
## 3. 💡 شرح المفردات
## 4. ✅ الأحكام والتوجيهات

**الحديث :**
## 1. 📖 نص الحديث
## 2. 📝 الراوي والمصدر
## 3. 💡 شرح المفردات
## 4. ✅ المعنى والدلالات

**العقيدة :**
## 1. 📝 المفهوم
## 2. 🔍 الأدلة
## 3. ✅ الشرح
## 4. 💡 التطبيق في الحياة

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
## 3. 💡 التطبيق العملي
## 4. ✅ الفوائد

⚠️ اعتمد على المذهب المالكي (المعتمد في المغرب).
أجب بالعربية الفصحى.
"""

PROMPT_COURS = """
Tu es un professeur de **{matiere}** au collège au Maroc.
Niveau : {niveau}
Langue : {langue}

📚 **Cours demandé** : {nom_cours}

Donne une explication COMPLÈTE :

## 1. 📖 Définition simple
## 2. 📐 Formules / Règles importantes
## 3. 💡 Exemples concrets (2-3)
## 4. 🎯 Méthode de résolution
## 5. ⚠️ Erreurs fréquentes à éviter
## 6. 🎯 Exercices d'application (avec solutions)
## 7. 📝 Résumé à retenir (Fiche mémo)
## 8. 🔗 Liens avec d'autres cours
## 9. 🇲🇦 Exemple du programme marocain
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

NOMS_MATIERES = {
    "math": {"fr": "Mathématiques", "ar": "الرياضيات", "icone": "📐"},
    "physique": {"fr": "Physique-Chimie", "ar": "الفيزياء والكيمياء", "icone": "⚗️"},
    "francais": {"fr": "Français", "ar": "اللغة الفرنسية", "icone": "🌍"},
    "arabe": {"fr": "Arabe", "ar": "اللغة العربية", "icone": "🕌"},
    "anglais": {"fr": "Anglais", "ar": "اللغة الإنجليزية", "icone": "🇬🇧"},
    "svt": {"fr": "SVT", "ar": "علوم الحياة والأرض", "icone": "📖"},
    "ijtima3iyat": {"fr": "Histoire-Géo", "ar": "الاجتماعيات", "icone": "🏛️"},
    "tarbia": {"fr": "Éducation Islamique", "ar": "التربية الإسلامية", "icone": "☪️"},
}

NIVEAUX = {
    "1ere_college": {"fr": "1ère année collège", "ar": "السنة الأولى إعدادي"},
    "2eme_college": {"fr": "2ème année collège", "ar": "السنة الثانية إعدادي"},
    "3eme_college": {"fr": "3ème année collège", "ar": "السنة الثالثة إعدادي"},
}


# ═══════════════════════════════════════════════════════════════════
# 🤖 SERVICE GEMINI
# ═══════════════════════════════════════════════════════════════════

class GeminiService:
    """Service unique pour appeler Gemini"""
    
    def __init__(self):
        self.model_name = MODEL_NAME
        self.generation_config = {
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
    
    def _get_model(self):
        """Créer un modèle Gemini"""
        return genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            system_instruction=SYSTEM_PROMPT
        )
    
    def _preparer_contenu(
        self,
        prompt_texte: str,
        image_bytes: bytes = None,
        fichier_bytes: bytes = None,
        type_fichier: str = None
    ) -> list:
        """Préparer contenu multimodal (texte + image + PDF)"""
        contenu = [prompt_texte]
        
        # Ajouter image
        if image_bytes:
            try:
                image = Image.open(io.BytesIO(image_bytes))
                contenu.append(image)
            except Exception as e:
                contenu.append(f"[Erreur image : {e}]")
        
        # Ajouter PDF (lu nativement par Gemini)
        elif fichier_bytes and type_fichier == "application/pdf":
            contenu.append({
                "mime_type": "application/pdf",
                "data": fichier_bytes
            })
        
        # Autres fichiers → texte
        elif fichier_bytes:
            try:
                texte = fichier_bytes.decode('utf-8', errors='ignore')
                contenu.append(f"\n\n--- Contenu du fichier ---\n{texte}")
            except:
                contenu.append("[Fichier non lisible]")
        
        return contenu
    
    def resoudre_exercice(
        self,
        matiere: str,
        niveau: str,
        langue: str,
        contenu_texte: str,
        image_bytes: bytes = None,
        fichier_bytes: bytes = None,
        type_fichier: str = None
    ) -> str:
        """Résoudre un exercice"""
        if matiere not in PROMPTS_MATIERES:
            raise ValueError(f"Matière non supportée : {matiere}")
        
        prompt = PROMPTS_MATIERES[matiere].format(
            niveau=niveau,
            langue=langue,
            contenu=contenu_texte or "[Voir pièce jointe]"
        )
        
        contenu = self._preparer_contenu(
            prompt, image_bytes, fichier_bytes, type_fichier
        )
        
        model = self._get_model()
        response = model.generate_content(contenu)
        return response.text
    
    def resoudre_multi_exercices(
        self,
        matiere: str,
        niveau: str,
        langue: str,
        exercices: list
    ) -> str:
        """Résoudre plusieurs exercices"""
        nom_matiere = NOMS_MATIERES[matiere]["fr"]
        
        intro = f"""
Tu es un professeur de {nom_matiere} au collège au Maroc.
Niveau : {niveau}
Langue : {langue}

Tu dois résoudre {len(exercices)} exercices SÉPARÉMENT.
Pour CHAQUE exercice, donne une solution complète et détaillée.
"""
        
        contenu = [intro]
        
        for i, ex in enumerate(exercices, 1):
            contenu.append(f"\n\n═══════════════════════════════")
            contenu.append(f"📝 EXERCICE N°{i}")
            contenu.append(f"═══════════════════════════════\n")
            
            if ex.get("texte"):
                contenu.append(ex["texte"])
            
            if ex.get("image_bytes"):
                try:
                    img = Image.open(io.BytesIO(ex["image_bytes"]))
                    contenu.append(img)
                except:
                    pass
        
        contenu.append("\n\nDonne maintenant les solutions séparées par :")
        contenu.append("═══ SOLUTION EXERCICE N°X ═══")
        
        model = self._get_model()
        response = model.generate_content(contenu)
        return response.text
    
    def expliquer_cours(
        self,
        nom_cours: str,
        matiere: str,
        niveau: str,
        langue: str
    ) -> str:
        """Expliquer un cours"""
        nom_matiere = NOMS_MATIERES.get(matiere, {}).get("fr", matiere)
        
        prompt = PROMPT_COURS.format(
            matiere=nom_matiere,
            niveau=niveau,
            langue=langue,
            nom_cours=nom_cours
        )
        
        model = self._get_model()
        response = model.generate_content(prompt)
        return response.text
    
    def poser_question(self, question: str, contexte: str = "") -> str:
        """Question libre"""
        prompt = f"{contexte}\n\n❓ Question : {question}" if contexte else question
        model = self._get_model()
        response = model.generate_content(prompt)
        return response.text


gemini_service = GeminiService()


# ═══════════════════════════════════════════════════════════════════
# 🚀 APPLICATION FASTAPI
# ═══════════════════════════════════════════════════════════════════

app = FastAPI(
    title="RévisoMaroc API",
    description="API de révision pour collégiens marocains (Powered by Google Gemini)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────
# 🏠 ENDPOINTS D'INFO
# ─────────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
async def root():
    return {
        "app": "RévisoMaroc API",
        "version": "1.0.0",
        "engine": "🤖 Google Gemini",
        "model": MODEL_NAME,
        "status": "✅ Actif",
        "matieres": list(NOMS_MATIERES.keys()),
        "endpoints": [
            "POST /solve          → Résoudre 1 exercice",
            "POST /solve-multi    → Résoudre plusieurs exercices",
            "POST /cours          → Expliquer un cours",
            "POST /question       → Poser une question libre",
            "GET  /matieres       → Liste des matières",
            "GET  /niveaux        → Liste des niveaux",
            "GET  /health         → État du serveur",
        ]
    }


@app.get("/health", tags=["Info"])
async def health():
    return {"status": "healthy", "engine": "gemini", "model": MODEL_NAME}


@app.get("/matieres", tags=["Info"])
async def lister_matieres():
    return {
        "matieres": [{"id": k, **v} for k, v in NOMS_MATIERES.items()]
    }


@app.get("/niveaux", tags=["Info"])
async def lister_niveaux():
    return {
        "niveaux": [{"id": k, **v} for k, v in NIVEAUX.items()]
    }


# ─────────────────────────────────────────────────────────────────
# 🎯 ENDPOINT 1 : RÉSOUDRE UN EXERCICE
# ─────────────────────────────────────────────────────────────────

@app.post("/solve", tags=["Exercices"])
async def resoudre_exercice(
    matiere: str = Form(..., description="math, physique, francais, arabe, anglais, svt, ijtima3iyat, tarbia"),
    niveau: str = Form("3eme_college"),
    langue: str = Form("fr", description="fr, ar, en"),
    texte: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    fichier: Optional[UploadFile] = File(None)
):
    """
    📚 Résoudre un exercice avec Gemini
    
    Accepte : texte, image (JPG/PNG), ou fichier (PDF/Word)
    """
    
    # Validations
    if matiere not in PROMPTS_MATIERES:
        raise HTTPException(400, f"Matière '{matiere}' non supportée. "
                                f"Disponibles : {list(PROMPTS_MATIERES.keys())}")
    
    if niveau not in NIVEAUX:
        raise HTTPException(400, f"Niveau '{niveau}' invalide")
    
    if not texte and not image and not fichier:
        raise HTTPException(400, "Fournir au moins : texte, image ou fichier")
    
    debut = time.time()
    
    try:
        image_bytes = None
        fichier_bytes = None
        type_fichier = None
        
        # Traiter image
        if image:
            image_bytes = await image.read()
            if len(image_bytes) > MAX_FILE_SIZE:
                raise HTTPException(400, "Image trop grande (max 20 MB)")
        
        # Traiter fichier
        if fichier:
            fichier_bytes = await fichier.read()
            if len(fichier_bytes) > MAX_FILE_SIZE:
                raise HTTPException(400, "Fichier trop grand (max 20 MB)")
            type_fichier = fichier.content_type
        
        # Appeler Gemini
        solution = gemini_service.resoudre_exercice(
            matiere=matiere,
            niveau=niveau,
            langue=langue,
            contenu_texte=texte or "",
            image_bytes=image_bytes,
            fichier_bytes=fichier_bytes,
            type_fichier=type_fichier
        )
        
        temps = round(time.time() - debut, 2)
        
        return {
            "success": True,
            "matiere": matiere,
            "matiere_nom": NOMS_MATIERES[matiere]["fr"],
            "niveau": niveau,
            "langue": langue,
            "solution": solution,
            "temps_traitement": f"{temps}s",
            "engine": "Google Gemini"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erreur Gemini : {str(e)}")


# ─────────────────────────────────────────────────────────────────
# 🎯 ENDPOINT 2 : RÉSOUDRE PLUSIEURS EXERCICES
# ─────────────────────────────────────────────────────────────────

@app.post("/solve-multi", tags=["Exercices"])
async def resoudre_multi(
    matiere: str = Form(...),
    niveau: str = Form("3eme_college"),
    langue: str = Form("fr"),
    textes: Optional[str] = Form(None, description="Textes séparés par '|||'"),
    images: Optional[List[UploadFile]] = File(None)
):
    """
    📚📚 Résoudre PLUSIEURS exercices (max 10)
    """
    
    if matiere not in PROMPTS_MATIERES:
        raise HTTPException(400, f"Matière '{matiere}' non supportée")
    
    exercices = []
    
    # Textes
    if textes:
        for t in textes.split("|||"):
            if t.strip():
                exercices.append({"texte": t.strip()})
    
    # Images
    if images:
        for img in images:
            data = await img.read()
            if len(data) > MAX_FILE_SIZE:
                raise HTTPException(400, "Image trop grande")
            exercices.append({"image_bytes": data})
    
    if not exercices:
        raise HTTPException(400, "Aucun exercice fourni")
    
    if len(exercices) > 10:
        raise HTTPException(400, "Maximum 10 exercices")
    
    debut = time.time()
    
    try:
        solution = gemini_service.resoudre_multi_exercices(
            matiere=matiere,
            niveau=niveau,
            langue=langue,
            exercices=exercices
        )
        
        temps = round(time.time() - debut, 2)
        
        return {
            "success": True,
            "matiere": matiere,
            "niveau": niveau,
            "nombre_exercices": len(exercices),
            "solution": solution,
            "temps_traitement": f"{temps}s"
        }
    
    except Exception as e:
        raise HTTPException(500, f"Erreur Gemini : {str(e)}")


# ─────────────────────────────────────────────────────────────────
# 🎯 ENDPOINT 3 : EXPLIQUER UN COURS
# ─────────────────────────────────────────────────────────────────

@app.post("/cours", tags=["Cours"])
async def expliquer_cours(
    nom_cours: str = Form(..., description="Ex: Théorème de Pythagore"),
    matiere: str = Form(...),
    niveau: str = Form("3eme_college"),
    langue: str = Form("fr")
):
    """
    📖 Expliquer un cours en détail
    
    L'élève donne le NOM du cours et reçoit une explication complète
    """
    
    if matiere not in PROMPTS_MATIERES:
        raise HTTPException(400, f"Matière '{matiere}' non supportée")
    
    if len(nom_cours.strip()) < 2:
        raise HTTPException(400, "Nom du cours trop court")
    
    debut = time.time()
    
    try:
        explication = gemini_service.expliquer_cours(
            nom_cours=nom_cours,
            matiere=matiere,
            niveau=niveau,
            langue=langue
        )
        
        temps = round(time.time() - debut, 2)
        
        return {
            "success": True,
            "cours": nom_cours,
            "matiere": matiere,
            "matiere_nom": NOMS_MATIERES[matiere]["fr"],
            "niveau": niveau,
            "explication": explication,
            "temps_traitement": f"{temps}s"
        }
    
    except Exception as e:
        raise HTTPException(500, f"Erreur Gemini : {str(e)}")


# ─────────────────────────────────────────────────────────────────
# 🎯 ENDPOINT 4 : QUESTION LIBRE (Chatbot)
# ─────────────────────────────────────────────────────────────────

@app.post("/question", tags=["Chatbot"])
async def poser_question(
    question: str = Form(...),
    contexte: str = Form(""),
    matiere: str = Form("math")
):
    """❓ Poser une question libre au professeur IA"""
    
    if len(question.strip()) < 3:
        raise HTTPException(400, "Question trop courte")
    
    try:
        contexte_complet = f"""
Tu es un professeur de {NOMS_MATIERES.get(matiere, {}).get('fr', matiere)} 
au collège au Maroc.
{contexte}
"""
        
        reponse = gemini_service.poser_question(question, contexte_complet)
        
        return {
            "success": True,
            "question": question,
            "reponse": reponse
        }
    
    except Exception as e:
        raise HTTPException(500, f"Erreur : {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# 🚀 LANCEMENT
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    print("""
╔═══════════════════════════════════════════════════════╗
║  🎓 RévisoMaroc API - Google Gemini                  ║
║  ─────────────────────────────────────────────────    ║
║  ✅ 8 matières supportées                            ║
║  ✅ Résolution d'exercices (texte/image/PDF)         ║
║  ✅ Explication de cours                             ║
║  ✅ Multi-exercices                                  ║
║  ─────────────────────────────────────────────────    ║
║  🌐 http://localhost:8000                            ║
║  📖 http://localhost:8000/docs                       ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
