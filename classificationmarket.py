import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 1000)

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'fills.csv.gz')

try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    try:
        df = pd.read_csv('fills.csv.gz')
    except FileNotFoundError:
        print("Erreur : Fichier fills.csv.gz introuvable.")
        exit()

df['side'] = df['side'].str.upper()
df['amount_usd'] = df['price'] * df['size']

df['buy_vol'] = np.where(df['side'] == 'BUY', df['amount_usd'], 0)
df['sell_vol'] = np.where(df['side'] == 'SELL', df['amount_usd'], 0)

traders = df.groupby('wallet').agg({
    'amount_usd': 'sum',
    'buy_vol': 'sum',
    'sell_vol': 'sum',
    'size': 'count'
}).rename(columns={'size': 'trade_count', 'amount_usd': 'total_volume'})

traders['avg_size'] = traders['total_volume'] / traders['trade_count']
traders['imbalance_ratio'] = abs(traders['buy_vol'] - traders['sell_vol']) / traders['total_volume']

def classify_trader(row):
    if row['trade_count'] > 50 and row['imbalance_ratio'] < 0.3:
        return 'Market Maker'
    
    if row['avg_size'] > 2000 or (row['total_volume'] > 50000 and row['imbalance_ratio'] > 0.6):
        return 'Whale'
    
    if row['avg_size'] < 100 and row['trade_count'] < 20:
        return 'Retail'
    
    return 'Regular Trader'

traders['classification'] = traders.apply(classify_trader, axis=1)

top_mms = traders[traders['classification'] == 'Market Maker'].sort_values('total_volume', ascending=False).head(1000)
csv_output = os.path.join(script_dir, 'top_1000_market_makers.csv')
top_mms.to_csv(csv_output)

print(f"Fichier CSV généré : {csv_output}")
print(top_mms[['total_volume', 'trade_count', 'imbalance_ratio']].head(5))

plt.figure(figsize=(12, 7))
sns.set_style("whitegrid")

ax = sns.countplot(
    data=traders,
    x='classification',
    hue='classification',
    palette='viridis',
    order=['Retail', 'Regular Trader', 'Whale', 'Market Maker'],
    legend=False
)

plt.yscale('log')
plt.title('Distribution des Traders', fontsize=16, fontweight='bold')
plt.ylabel('Nombre de Traders (Log)', fontsize=12)
plt.xlabel('Catégorie', fontsize=12)

for p in ax.patches:
    height = p.get_height()
    if height > 0:
        ax.annotate(f'{int(height)}',
                    (p.get_x() + p.get_width() / 2., height),
                    ha='center', va='bottom',
                    fontsize=11, color='black',
                    xytext=(0, 5),
                    textcoords='offset points')

img_output = os.path.join(script_dir, 'trader_classification_histogram.png')
plt.tight_layout()
plt.savefig(img_output)

print(f"Graphique généré : {img_output}")
