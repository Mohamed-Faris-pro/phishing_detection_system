import os
import joblib
import pandas as pd
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import google.generativeai as genai
from dotenv import load_dotenv
from .ml_utils import extract_features
from .models import ScanHistory
from .serializers import ScanHistorySerializer
from django.db.models import Count

# Chargement de la clé depuis le fichier secret .env
load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# Configuration de Gemini
if GEMINI_KEY and GEMINI_KEY != "METTRE_TA_CLE_ICI":
    genai.configure(api_key=GEMINI_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.5-flash')
else:
    gemini_model = None

# Pointage vers le dossier de modèles
MODELS_DIR = os.path.join(settings.BASE_DIR.parent, 'ml_core', 'models')
URL_MODEL_PATH = os.path.join(MODELS_DIR, 'voting_phishing_url_model.pkl')
EMAIL_MODEL_PATH = os.path.join(MODELS_DIR, 'voting_email_model.pkl')
TFIDF_PATH = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')


class AnalyzeView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        data = request.data
        text_content = data.get('content', '')
        scan_type = data.get('type', 'url')
        
        if not text_content:
            return Response({"error": "Le contenu à analyser est vide."}, status=400)

        try:
            # 1. PRÉDICTION MACHINE LEARNING LOCALE
            if scan_type == 'url':
                model = joblib.load(URL_MODEL_PATH)
                features = extract_features(text_content)
                X_input = pd.DataFrame([features])
                prediction = model.predict(X_input)[0]
                xgb_model = model.named_estimators_['xgb']
                proba_arr = xgb_model.predict_proba(X_input)[0]
                risk_score = round(float(proba_arr[1]) * 100, 2)
            else:
                model = joblib.load(EMAIL_MODEL_PATH)
                vectorizer = joblib.load(TFIDF_PATH)
                X_input = vectorizer.transform([text_content])
                prediction = model.predict(X_input)[0]
                xgb_model = model.named_estimators_['xgb']
                proba_arr = xgb_model.predict_proba(X_input)[0]
                risk_score = round(float(proba_arr[1]) * 100, 2)

            is_phishing = bool(prediction == 1)

            # 2. APPEL A L'IA GEMINI SI DANGER DETECTE
            explanation = "Cet élément ne présente aucune caractéristique suspecte mathématique."
            
            if is_phishing:
                if gemini_model:
                    try:
                        prompt = f"""Tu es un expert en cybersécurité. Le système de Machine Learning suspecte que ce contenu ({scan_type}) est du phishing avec un score de {risk_score}%.
Analyse ce contenu de manière approfondie.
Tu DOIS répondre UNIQUEMENT avec un objet JSON valide contenant exactement deux clés :
1. "final_verdict": "PHISHING" (si tu confirmes la menace) ou "SÉCURISÉ" (si c'est un faux positif du ML).
2. "explanation": "Ton explication concise (2 phrases) pour l'utilisateur final."

Contenu à analyser : '{text_content}'"""
                        
                        # On force Gemini à répondre en format JSON
                        response = gemini_model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                        
                        import json
                        ai_data = json.loads(response.text)
                        explanation = ai_data.get("explanation", response.text)
                        
                        # Si l'IA Générative détermine que c'est sécurisé, elle ÉCRASE le verdict du ML !
                        if ai_data.get("final_verdict") == "SÉCURISÉ":
                            is_phishing = False
                            risk_score = min(risk_score, 25.0) # On abaisse le score car l'IA a corrigé le tir
                            
                    except Exception as gemini_err:
                        explanation = "Contenu malveillant détecté ! (Note: Impossible de générer l'explication détaillée, l'API IA est indisponible)."
                else:
                    explanation = "Attention, contenu suspect détecté ! (Astuce développeur : Renseigne ta clé API Gemini dans backend/.env)."

            verdict_str = "PHISHING" if is_phishing else "SÉCURISÉ"

            # 3. SAUVEGARDE DANS LA BASE DE DONNÉES (POUR L'HISTORIQUE ET LE DASHBOARD)
            ScanHistory.objects.create(
                scan_type=scan_type,
                content=text_content,
                verdict=verdict_str,
                risk_score=risk_score,
                explanation=explanation
            )

            return Response({
                "verdict": verdict_str,
                "risk_score": risk_score,
                "explanation": explanation
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class HistoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        history = ScanHistory.objects.all()[:50] # On récupère les 50 derniers scans
        serializer = ScanHistorySerializer(history, many=True)
        return Response(serializer.data)


class DashboardStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        total_scans = ScanHistory.objects.count()
        phishing_count = ScanHistory.objects.filter(verdict="PHISHING").count()
        safe_count = ScanHistory.objects.filter(verdict="SÉCURISÉ").count()
        
        url_phishing = ScanHistory.objects.filter(scan_type="url", verdict="PHISHING").count()
        email_phishing = ScanHistory.objects.filter(scan_type="email", verdict="PHISHING").count()

        return Response({
            "total_scans": total_scans,
            "phishing_count": phishing_count,
            "safe_count": safe_count,
            "threat_vectors": [
                {"name": "URLs Malveillantes", "value": url_phishing},
                {"name": "E-mails Malveillants", "value": email_phishing}
            ]
        })
