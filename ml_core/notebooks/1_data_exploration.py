import pandas as pd
import os

# Chemins des fichiers
DATA_DIR = '../data'
URLS_FILE = os.path.join(DATA_DIR, 'dataset_phishing.csv')
EMAILS_FILE = os.path.join(DATA_DIR, 'spam_ham_dataset.csv')
USELESS_FILE = os.path.join(DATA_DIR, 'emails.csv')

# --- NETTOYAGE DES FICHIERS INUTILES ---
if os.path.exists(USELESS_FILE):
    os.remove(USELESS_FILE)
    print(f"Fichier inutile supprimé : {USELESS_FILE}\n")

print("=== 1. NETTOYAGE ET ÉQUILIBRAGE DES URLs ===")
df_urls = pd.read_csv(URLS_FILE)

# On garde uniquement l'URL brute et le label
df_urls = df_urls[['url', 'status']]

# Suppression des valeurs nulles et doublons
df_urls = df_urls.dropna().drop_duplicates()

# ÉQUILIBRAGE DES CLASSES (Undersampling de la classe majoritaire)
min_class_size = df_urls['status'].value_counts().min()
df_urls_balanced = pd.concat([
    df_urls[df_urls['status'] == 'legitimate'].sample(min_class_size, random_state=42),
    df_urls[df_urls['status'] == 'phishing'].sample(min_class_size, random_state=42)
])
# On mélange (shuffle) les données
df_urls_balanced = df_urls_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

print("Répartition des classes (URLs) APRÈS équilibrage :")
print(df_urls_balanced['status'].value_counts())


print("\n=== 2. NETTOYAGE ET ÉQUILIBRAGE DES E-MAILS ===")
df_emails = pd.read_csv(EMAILS_FILE)

# Standardisation des colonnes
df_emails = df_emails[['text', 'label_num']]
df_emails.columns = ['email_text', 'is_phishing']

# Suppression des valeurs nulles et doublons
df_emails = df_emails.dropna().drop_duplicates()

# ÉQUILIBRAGE DES CLASSES (Undersampling)
min_email_size = df_emails['is_phishing'].value_counts().min()
df_emails_balanced = pd.concat([
    df_emails[df_emails['is_phishing'] == 0].sample(min_email_size, random_state=42),
    df_emails[df_emails['is_phishing'] == 1].sample(min_email_size, random_state=42)
])
# On mélange (shuffle)
df_emails_balanced = df_emails_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

print("Répartition des classes (E-mails) APRÈS équilibrage :")
print(df_emails_balanced['is_phishing'].value_counts().replace({0: 'Légitime', 1: 'Phishing'}))

# --- SAUVEGARDE ---
df_urls_balanced.to_csv(os.path.join(DATA_DIR, 'cleaned_urls.csv'), index=False)
df_emails_balanced.to_csv(os.path.join(DATA_DIR, 'cleaned_emails.csv'), index=False)
print("\n[OK] Données nettoyées, ÉQUILIBRÉES et sauvegardées avec succès !")
