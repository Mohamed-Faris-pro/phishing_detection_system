import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Création du dossier pour les images
PLOTS_DIR = '../plots'
os.makedirs(PLOTS_DIR, exist_ok=True)

# Configuration du style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12

# Données des URLs
url_models = ['SVM', 'Random Forest', 'XGBoost', 'Vote Majoritaire']
url_accuracy = [73.71, 82.33, 83.29, 82.81]
url_f1 = [67.10, 82.23, 82.68, 82.80]

# Données des E-mails
email_models = ['SVM', 'Random Forest', 'XGBoost', 'Vote Majoritaire']
email_accuracy = [97.44, 97.95, 97.44, 98.00]
email_f1 = [97.32, 97.85, 97.31, 97.90]

def plot_metric(models, scores, title, ylabel, filename, color):
    plt.figure()
    ax = sns.barplot(x=models, y=scores, palette=color)
    plt.title(title, fontsize=14, pad=15, fontweight='bold')
    plt.ylabel(ylabel, fontsize=12)
    plt.ylim(0, 100)
    
    # Ajouter les valeurs sur les barres
    for i, v in enumerate(scores):
        ax.text(i, v + 1, f"{v}%", ha='center', va='bottom', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, filename), dpi=300)
    plt.close()

# Génération des 4 graphes
plot_metric(url_models, url_accuracy, 'Accuracy des Modèles (Détection d\'URLs)', 'Accuracy (%)', 'url_accuracy.png', 'Blues_d')
plot_metric(url_models, url_f1, 'F1-Score des Modèles (Détection d\'URLs)', 'F1-Score (%)', 'url_f1.png', 'Greens_d')

plot_metric(email_models, email_accuracy, 'Accuracy des Modèles (Détection d\'E-mails)', 'Accuracy (%)', 'email_accuracy.png', 'Purples_d')
plot_metric(email_models, email_f1, 'F1-Score des Modèles (Détection d\'E-mails)', 'F1-Score (%)', 'email_f1.png', 'Oranges_d')

print(f"Les 4 graphiques ont été générés avec succès dans le dossier : {PLOTS_DIR}")
