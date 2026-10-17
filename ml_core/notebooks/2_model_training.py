import os
import pandas as pd
import numpy as np
import re
import math
import ipaddress
import joblib
from urllib.parse import urlparse
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

DATA_DIR = '../data'
MODELS_DIR = '../models'
os.makedirs(MODELS_DIR, exist_ok=True)

print("=== PARTIE 1 : FEATURE ENGINEERING ENRICHI DES URLs ===")

def is_ip_address(url):
    domain = urlparse(url).netloc
    if not domain:
        domain = urlparse('http://'+url).netloc
    domain = domain.split(':')[0]
    try:
        ipaddress.ip_address(domain)
        return 1
    except ValueError:
        return 0

def calculate_entropy(text):
    if not text: return 0
    prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
    return -sum(p * math.log(p) / math.log(2.0) for p in prob)

def extract_features(url):
    url_lower = str(url).lower()
    parsed = urlparse('http://' + url_lower if not url_lower.startswith('http') else url_lower)
    
    suspicious_words = ['login', 'verify', 'update', 'secure', 'bank', 'account', 'auth', 'confirm', 'service']
    has_suspicious_word = sum(1 for word in suspicious_words if word in url_lower)
    
    suspicious_tlds = ['.xyz', '.top', '.tk', '.ml', '.ga', '.cf', '.gq', '.cc']
    has_suspicious_tld = sum(1 for tld in suspicious_tlds if url_lower.endswith(tld) or tld + '/' in url_lower)
    
    return {
        'length_url': len(url_lower),
        'length_hostname': len(parsed.netloc),
        'length_path': len(parsed.path),
        'count_dot': url_lower.count('.'),
        'count_hyphen': url_lower.count('-'),
        'count_at': url_lower.count('@'),
        'count_query': url_lower.count('?'),
        'count_equal': url_lower.count('='),
        'count_underscore': url_lower.count('_'),
        'count_percent': url_lower.count('%'),
        'count_ampersand': url_lower.count('&'),
        'count_digits': sum(c.isdigit() for c in url_lower),
        'has_ip': is_ip_address(url_lower),
        'has_suspicious_word': has_suspicious_word,
        'has_suspicious_tld': has_suspicious_tld,
        'entropy': calculate_entropy(url_lower)
    }

df_urls = pd.read_csv(os.path.join(DATA_DIR, 'cleaned_urls.csv'))
print(f"Calcul instantané de {len(extract_features('test.com'))} caractéristiques pour chaque URL...")

features_df = pd.DataFrame(df_urls['url'].apply(extract_features).tolist())
X_urls = features_df
y_urls = df_urls['status'].apply(lambda x: 1 if x == 'phishing' else 0)

X_train_u, X_test_u, y_train_u, y_test_u = train_test_split(X_urls, y_urls, test_size=0.2, random_state=42)

def evaluate_model(name, model, X_train, y_train, X_test, y_test):
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    print(f"\n--- {name} ---")
    print(f"Accuracy  : {accuracy_score(y_test, preds)*100:.2f}%")
    print(f"F1-Score  : {f1_score(y_test, preds)*100:.2f}%")
    return model

print("\nEntraînement des modèles sur les URLs...")
rf_url = evaluate_model("Random Forest (URLs)", RandomForestClassifier(n_estimators=100, random_state=42), X_train_u, y_train_u, X_test_u, y_test_u)
svm_url = evaluate_model("SVM (URLs)", SVC(kernel='linear', random_state=42), X_train_u, y_train_u, X_test_u, y_test_u)
xgb_url = evaluate_model("XGBoost (URLs)", XGBClassifier(eval_metric='logloss', random_state=42), X_train_u, y_train_u, X_test_u, y_test_u)

print("\nFusion des 3 modèles en un VotingClassifier (Vote Majoritaire)...")
voting_url = VotingClassifier(estimators=[('rf', rf_url), ('svm', svm_url), ('xgb', xgb_url)], voting='hard')
voting_url.fit(X_train_u, y_train_u)
preds_voting_u = voting_url.predict(X_test_u)
print(f"Accuracy (Voting URL) : {accuracy_score(y_test_u, preds_voting_u)*100:.2f}%")

joblib.dump(voting_url, os.path.join(MODELS_DIR, 'voting_phishing_url_model.pkl'))
print(f"[+] Modèle Voting (URLs) sauvegardé !")


print("\n\n=== PARTIE 2 : NLP (TF-IDF) DES E-MAILS ===")
df_emails = pd.read_csv(os.path.join(DATA_DIR, 'cleaned_emails.csv')).dropna()

X_text = df_emails['email_text']
y_emails = df_emails['is_phishing']

print("Vectorisation TF-IDF en cours...")
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
X_tfidf = vectorizer.fit_transform(X_text)

X_train_e, X_test_e, y_train_e, y_test_e = train_test_split(X_tfidf, y_emails, test_size=0.2, random_state=42)

print("\nEntraînement des modèles sur les E-mails...")
rf_email = evaluate_model("Random Forest (E-mails)", RandomForestClassifier(n_estimators=100, random_state=42), X_train_e, y_train_e, X_test_e, y_test_e)
svm_email = evaluate_model("SVM (E-mails)", SVC(kernel='linear', random_state=42), X_train_e, y_train_e, X_test_e, y_test_e)
xgb_email = evaluate_model("XGBoost (E-mails)", XGBClassifier(eval_metric='logloss', random_state=42), X_train_e, y_train_e, X_test_e, y_test_e)

print("\nFusion des 3 modèles en un VotingClassifier (Vote Majoritaire)...")
voting_email = VotingClassifier(estimators=[('rf', rf_email), ('svm', svm_email), ('xgb', xgb_email)], voting='hard')
voting_email.fit(X_train_e, y_train_e)

joblib.dump(vectorizer, os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl'))
joblib.dump(voting_email, os.path.join(MODELS_DIR, 'voting_email_model.pkl'))
print(f"[+] Vectoriseur et Modèle Voting (E-mails) sauvegardés dans {MODELS_DIR}")
print("\n[OK] Étape 2 terminée !")
