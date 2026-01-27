import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# ==========================================
# 1. CHARGEMENT ROBUSTE
# ==========================================
# Cette astuce permet de trouver le fichier peu importe où vous êtes dans le terminal
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'fills.csv.gz')

print(f"Chargement du fichier : {file_path}...")

try:
    df = pd.read_csv(file_path)
    print(f"Succès ! {len(df)} transactions chargées.")
    
except FileNotFoundError:
    # Si la méthode automatique échoue, on tente le chemin direct (cas où vous êtes dans le dossier)
    try:
        df = pd.read_csv('fills.csv.gz')
        print(f"Succès (chemin direct) ! {len(df)} transactions chargées.")
    except FileNotFoundError:
        print("Erreur : Impossible de trouver 'fills.csv.gz'.")
        print("Assurez-vous que le fichier est dans le même dossier que ce script.")
        exit()

# ==========================================
# 2. PRÉPARATION DES DONNÉES (Fixé)
# ==========================================
print("Calcul des volumes...")

# On définit manuellement les colonnes car on les connait maintenant
user_col = 'wallet'

# CALCUL DU MONTANT EN DOLLARS (Important !)
# Volume ($) = Prix * Quantité
# Si on utilisait juste 'size', acheter 1000 actions à 1 centime semblerait énorme.
df['amount_usd'] = df['price'] * df['size']

# ==========================================
# 3. CALCUL DES PROFILS TRADERS
# ==========================================
print("Analyse des profils utilisateurs...")

user_stats = df.groupby(user_col).agg({
    'amount_usd': ['count', 'sum', 'mean']
})

user_stats.columns = ['trade_count', 'total_volume', 'avg_size']
user_stats = user_stats.fillna(0)

# Classification
def classify_user(row):
    # Seuils (Ajustables selon votre marché)
    WHALE_SIZE_THRESHOLD = 5000    # Ticket moyen > 5000$ (Baleine)
    MM_COUNT_THRESHOLD = 1000      # Plus de 1000 trades (Probablement un algo/MM)
    RETAIL_SIZE_LIMIT = 100        # Ticket moyen < 100$ (Petit porteur)

    if row['trade_count'] > MM_COUNT_THRESHOLD:
        return 'Market Maker'
    
    if row['avg_size'] > WHALE_SIZE_THRESHOLD:
        return 'Whale'
    
    if row['avg_size'] < RETAIL_SIZE_LIMIT and row['trade_count'] < 50:
        return 'Retail / Stupid Money'
        
    return 'Regular Trader'

user_stats['category'] = user_stats.apply(classify_user, axis=1)

print("\nRépartition trouvée :")
print(user_stats['category'].value_counts())

# ==========================================
# 4. GRAPHIQUE
# ==========================================
plt.figure(figsize=(12, 7))
sns.set_style("whitegrid")

# Histogramme
ax = sns.countplot(
    data=user_stats,
    x='category',
    hue='category',
    palette='viridis',
    order=['Retail / Stupid Money', 'Regular Trader', 'Whale', 'Market Maker'],
    legend=False
)

plt.yscale('log') # Indispensable car il y a souvent 1000x plus de retails que de whales
plt.title('Trader Classification (Based on real Fills)', fontsize=16, fontweight='bold')
plt.ylabel('Number of Traders (Log Scale)', fontsize=12)
plt.xlabel('Category', fontsize=12)

# Ajout des chiffres au dessus des barres
for p in ax.patches:
    height = p.get_height()
    if height > 0:
        ax.annotate(f'{int(height)}',
                    (p.get_x() + p.get_width() / 2., height),
                    ha='center', va='bottom',
                    fontsize=11, color='black',
                    xytext=(0, 5),
                    textcoords='offset points')

plt.tight_layout()
output_file = os.path.join(script_dir, 'trader_fills_analysis.png')
plt.savefig(output_file)
plt.show()

print(f"Graphique généré avec succès : {output_file}")