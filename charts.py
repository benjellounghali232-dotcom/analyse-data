import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

possible_files = ['analysis_results.csv', 'resultats_analyse.csv']
file_path = None

for fname in possible_files:
    temp_path = os.path.join(script_dir, fname)
    if os.path.exists(temp_path):
        file_path = temp_path
        break

if not file_path:
    for fname in possible_files:
        temp_path = os.path.join(script_dir, '..', fname)
        if os.path.exists(temp_path):
            file_path = temp_path
            break

if not file_path:
    print(f"Error: Could not find 'analysis_results.csv' or 'resultats_analyse.csv' in {script_dir}")
    exit()

print(f"Loading data from: {file_path}")
df = pd.read_csv(file_path)
df = df.drop_duplicates(subset=['slug'])
print(f"Data loaded: {len(df)} unique markets.")

def categorize_domain(row):
    text = (str(row.get('question', '')) + " " + str(row.get('slug', ''))).lower()
    
    if any(x in text for x in ['nfl', 'nba', 'football', 'soccer', 'tennis', 'super bowl', 'league', 'cup', 'winner', 'match', 'vs.', 'f1', 'prix']):
        return 'Sports'
    
    if any(x in text for x in ['bitcoin', 'btc', 'eth', 'solana', 'crypto', 'token', 'nft', 'wallet', 'chain', 'price of']):
        if 'bitcoin' in text or 'eth' in text or 'solana' in text or 'crypto' in text:
            return 'Crypto'
            
    if any(x in text for x in ['trump', 'biden', 'harris', 'election', 'vote', 'president', 'nominate', 'senate', 'house', 'republican', 'democrat']):
        return 'Politics (USA)'
        
    if any(x in text for x in ['war', 'strike', 'israel', 'iran', 'gaza', 'ukraine', 'russia', 'china', 'maduro', 'venezuela', 'military', 'invasion', 'ceasefire']):
        return 'Geopolitics'
        
    if any(x in text for x in ['fed', 'rate', 'inflation', 's&p', 'spx', 'nasdaq', 'stock', 'earnings', 'recession', 'bank', 'economy', 'shutdown']):
        return 'Economy'
        
    if any(x in text for x in ['tweet', 'twitter', 'elon', 'musk', 'movie', 'song', 'spotify', 'grammy', 'oscar', 'award', 'weather']):
        return 'Culture & Tech'
        
    return 'Other'

df['domain'] = df.apply(categorize_domain, axis=1)

AVG_DURATION_DAYS = 30
SPREAD_MARGIN = 0.005

df['est_daily_volume'] = df['total_volume'] / AVG_DURATION_DAYS
df['est_spread_revenue'] = df['est_daily_volume'] * SPREAD_MARGIN

stats = df.groupby('domain').agg({
    'daily_reward_usdc': 'sum',
    'total_volume': 'sum',
    'est_spread_revenue': 'sum'
}).sort_values('daily_reward_usdc', ascending=False)

fig1, axes = plt.subplots(1, 2, figsize=(18, 10))
colors = sns.color_palette("pastel")

axes[0].pie(stats['daily_reward_usdc'], labels=stats.index, autopct='%1.1f%%', startangle=140, colors=colors, pctdistance=0.85)
axes[0].add_artist(plt.Circle((0,0),0.70,fc='white')) 
axes[0].set_title('Market Share (Salaries / Rewards)', fontsize=16, fontweight='bold', pad=20)

stats_vol = stats.sort_values('total_volume', ascending=False)
axes[1].pie(stats_vol['total_volume'], labels=stats_vol.index, autopct='%1.1f%%', startangle=140, colors=colors, pctdistance=0.85)
axes[1].add_artist(plt.Circle((0,0),0.70,fc='white'))
axes[1].set_title('Volume Share (Total Activity)', fontsize=16, fontweight='bold', pad=20)

plt.subplots_adjust(top=0.85)
img_path1 = os.path.join(script_dir, 'market_share_english.png')
plt.savefig(img_path1, bbox_inches='tight', pad_inches=0.2)

plt.figure(figsize=(14, 8))
sns.set_theme(style="whitegrid")

stats_spread = stats.sort_values('est_spread_revenue', ascending=False)

barplot = sns.barplot(x=stats_spread['est_spread_revenue'], y=stats_spread.index, palette="viridis")

max_val = stats_spread['est_spread_revenue'].max()
plt.xlim(0, max_val * 1.2)

plt.title('Estimated Spread Revenue by Domain ($/day)', fontsize=18, fontweight='bold', pad=20)
plt.xlabel('Estimated Daily Revenue (USDC)', fontsize=14)
plt.ylabel('Domain', fontsize=14)

for i, v in enumerate(stats_spread['est_spread_revenue']):
    barplot.text(v + (v * 0.01), i, f" ${v:,.0f}", color='black', va='center', fontweight='bold', fontsize=11)

plt.tight_layout()
img_path2 = os.path.join(script_dir, 'spread_revenue_english.png')
plt.savefig(img_path2, bbox_inches='tight', pad_inches=0.2)

print("Charts generated successfully:")
print(f"1. {img_path1}")
print(f"2. {img_path2}")
