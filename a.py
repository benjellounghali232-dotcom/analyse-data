import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

try:
    print("Loading file...")
    df = pd.read_csv('resultats_analyse.csv')
    df = df.drop_duplicates(subset=['slug'])
    print(f"Data loaded: {len(df)} unique markets.")

except FileNotFoundError:
    print("Error: The file 'resultats_analyse.csv' was not found.")
    exit()

def categorize_domain(row):
    text = (str(row['question']) + " " + str(row['slug'])).lower()
    
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

fig1, axes = plt.subplots(1, 2, figsize=(16, 8))
colors = sns.color_palette("pastel")

axes[0].pie(stats['daily_reward_usdc'], labels=stats.index, autopct='%1.1f%%', startangle=140, colors=colors, pctdistance=0.85)
axes[0].add_artist(plt.Circle((0,0),0.70,fc='white')) 
axes[0].set_title('Where does Polymarket pay?\n(Rewards/Salaries Share)', fontsize=14, fontweight='bold')

stats_vol = stats.sort_values('total_volume', ascending=False)
axes[1].pie(stats_vol['total_volume'], labels=stats_vol.index, autopct='%1.1f%%', startangle=140, colors=colors, pctdistance=0.85)
axes[1].add_artist(plt.Circle((0,0),0.70,fc='white'))
axes[1].set_title('Where are the bettors?\n(Total Volume Share)', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))
sns.set_theme(style="whitegrid")

stats_spread = stats.sort_values('est_spread_revenue', ascending=False)

barplot = sns.barplot(x=stats_spread['est_spread_revenue'], y=stats_spread.index, palette="viridis")

plt.title('Estimated Spread Revenue Distribution ($/day)\n(The "Risk Premium")', fontsize=16, fontweight='bold')
plt.xlabel('Estimated Daily Revenue (USDC)', fontsize=12)
plt.ylabel('Domain', fontsize=12)

for i, v in enumerate(stats_spread['est_spread_revenue']):
    barplot.text(v + (v * 0.01), i, f" ${v:,.0f}", color='black', va='center', fontweight='bold')

plt.tight_layout()
plt.show()

