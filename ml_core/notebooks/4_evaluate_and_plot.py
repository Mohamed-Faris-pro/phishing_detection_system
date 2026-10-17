import os
import pandas as pd
import numpy as np
import math
import ipaddress
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from urllib.parse import urlparse
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

DATA_DIR = '../data'
MODELS_DIR = '../models'
PLOTS_DIR = '../plots'
os.makedirs(PLOTS_DIR, exist_ok=True)

# --- 1. FONCTIONS ET DONNEES ---
def is_ip_address(url):
    domain = urlparse(url).netloc
    if not domain: domain = urlparse('http://'+url).netloc
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
    suspicious_tlds = ['.xyz', '.top', '.tk', '.ml', '.ga', '.cf', '.gq', '.cc']
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
        'has_suspicious_word': sum(1 for w in suspicious_words if w in url_lower),
        'has_suspicious_tld': sum(1 for tld in suspicious_tlds if url_lower.endswith(tld) or tld + '/' in url_lower),
        'entropy': calculate_entropy(url_lower)
    }

print("Chargement des données de test...")
df_urls = pd.read_csv(os.path.join(DATA_DIR, 'cleaned_urls.csv'))
X_urls = pd.DataFrame(df_urls['url'].apply(extract_features).tolist())
y_urls = df_urls['status'].apply(lambda x: 1 if x == 'phishing' else 0)
_, X_test_u, _, y_test_u = train_test_split(X_urls, y_urls, test_size=0.2, random_state=42)

df_emails = pd.read_csv(os.path.join(DATA_DIR, 'cleaned_emails.csv')).dropna()
vectorizer = joblib.load(os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl'))
X_tfidf = vectorizer.transform(df_emails['email_text'])
_, X_test_e, _, y_test_e = train_test_split(X_tfidf, df_emails['is_phishing'], test_size=0.2, random_state=42)

# --- 2. EVALUATION ---
def get_metrics(model, X_test, y_test):
    preds = model.predict(X_test)
    return [
        accuracy_score(y_test, preds)*100,
        precision_score(y_test, preds)*100,
        recall_score(y_test, preds)*100,
        f1_score(y_test, preds)*100
    ]

print("Évaluation des modèles URL...")
voting_url = joblib.load(os.path.join(MODELS_DIR, 'voting_phishing_url_model.pkl'))
# To get the underlying models from voting classifier:
rf_url = voting_url.named_estimators_['rf']
svm_url = voting_url.named_estimators_['svm']
xgb_url = voting_url.named_estimators_['xgb']

url_data = {
    'Random Forest': get_metrics(rf_url, X_test_u, y_test_u),
    'SVM': get_metrics(svm_url, X_test_u, y_test_u),
    'XGBoost': get_metrics(xgb_url, X_test_u, y_test_u),
    'Vote Majoritaire': get_metrics(voting_url, X_test_u, y_test_u)
}

print("Évaluation des modèles E-mail...")
voting_email = joblib.load(os.path.join(MODELS_DIR, 'voting_email_model.pkl'))
rf_email = voting_email.named_estimators_['rf']
svm_email = voting_email.named_estimators_['svm']
xgb_email = voting_email.named_estimators_['xgb']

email_data = {
    'Random Forest': get_metrics(rf_email, X_test_e, y_test_e),
    'SVM': get_metrics(svm_email, X_test_e, y_test_e),
    'XGBoost': get_metrics(xgb_email, X_test_e, y_test_e),
    'Vote Majoritaire': get_metrics(voting_email, X_test_e, y_test_e)
}

# --- 3. GENERATION DES GRAPHES GROUPÉS ---
def plot_grouped_metrics(data_dict, title, filename):
    sns.set_theme(style="whitegrid")
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    models = list(data_dict.keys())
    
    # Transformation en DataFrame pour Seaborn
    rows = []
    for model_name, scores in data_dict.items():
        for i, metric_name in enumerate(metrics):
            rows.append({'Model': model_name, 'Metric': metric_name, 'Score': scores[i]})
    
    df_plot = pd.DataFrame(rows)
    
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(data=df_plot, x='Model', y='Score', hue='Metric', palette='viridis')
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('Score (%)', fontsize=12)
    plt.ylim(0, 110)
    
    # Ajout des valeurs
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f', padding=3, fontsize=9)
        
    plt.legend(title='Métriques', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

plot_grouped_metrics(url_data, "Évaluation Globale des Modèles (Détection d'URLs)", "url_all_metrics.png")
plot_grouped_metrics(email_data, "Évaluation Globale des Modèles (Détection d'E-mails)", "email_all_metrics.png")

print("Graphiques globaux générés avec succès !")
