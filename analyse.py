import json
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
INPUT_FILE = 'markets.jsonl'  # Le nom de votre fichier de 2 Go
OUTPUT_FILE = 'resultats_analyse.csv'
CHUNK_SIZE = 10000  # Nombre de lignes traitées à la fois pour économiser la mémoire

def process_markets_file(file_path):
    print(f"🚀 Démarrage de l'analyse du fichier : {file_path}")
    
    # Stockage des résultats
    market_data = []
    
    # Compteurs pour le suivi
    total_lines = 0
    markets_with_rewards = 0
    
    try:
        # Ouverture du fichier en mode lecture ligne par ligne
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                total_lines += 1
                if total_lines % 50000 == 0:
                    print(f"⏳ {total_lines} marchés traités...")
                
                try:
                    data = json.loads(line)
                    
                    # --- EXTRACTION DES DONNÉES CLÉS ---
                    
                    # 1. Infos de base
                    question = data.get('question', 'N/A')
                    market_slug = data.get('slug', 'N/A')
                    active = data.get('active', False)
                    volume = float(data.get('volume', 0))
                    
                    # 2. Identification du Market Maker officiel (si présent)
                    mm_address = data.get('marketMakerAddress', None)
                    
                    # 3. Analyse des Récompenses (Rewards)
                    # C'est ici qu'on voit combien le marché paie les MMs
                    daily_reward = 0
                    reward_asset = "N/A"
                    
                    # La structure des rewards est souvent imbriquée dans 'clobRewards'
                    clob_rewards = data.get('clobRewards', [])
                    if clob_rewards and isinstance(clob_rewards, list):
                        for reward in clob_rewards:
                            # On convertit en float et on gère les cas vides
                            rate = reward.get('rewardsDailyRate', 0)
                            if rate:
                                daily_reward += float(rate)
                                reward_asset = reward.get('assetAddress', 'Unknown')
                                markets_with_rewards += 1

                    # 4. On garde uniquement les marchés intéressants 
                    # (Soit du volume, soit des rewards, soit un MM identifié)
                    if volume > 1000 or daily_reward > 0 or mm_address:
                        market_data.append({
                            'question': question,
                            'slug': market_slug,
                            'active': active,
                            'total_volume': volume,
                            'daily_reward_usdc': daily_reward,
                            'mm_address': mm_address,
                            'reward_asset': reward_asset
                        })
                        
                except json.JSONDecodeError:
                    continue # Ignore les lignes mal formées

    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {file_path} est introuvable.")
        return

    # --- GÉNÉRATION DU RAPPORT ---
    print(f"\n Analyse terminée. {total_lines} lignes scannées.")
    
    if market_data:
        df = pd.DataFrame(market_data)
        
        # Tri par récompense journalière (Les plus rentables d'abord)
        df = df.sort_values(by='daily_reward_usdc', ascending=False)
        
        # Sauvegarde
        df.to_csv(OUTPUT_FILE, index=False)
        print(f" Résultats sauvegardés dans : {OUTPUT_FILE}")
        print("\n--- TOP 5 DES MARCHÉS LES PLUS RENTABLES (REWARDS) ---")
        print(df[['question', 'daily_reward_usdc', 'total_volume']].head(5).to_string())
    else:
        print(" Aucune donnée pertinente trouvée.")

if __name__ == "__main__":
    process_markets_file(INPUT_FILE)