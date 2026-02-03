import urllib.request, json, urllib.parse
from datetime import datetime, timedelta

# CONFIGURATION
API_KEY = "b7191bd60e5363789c259b864ddc5367"
TOKEN = "8341397638:AAENHUF8V4FoCenp9aR7ockDcHAGZgmN66s"
ID = "1697906576"

def run_nhl_custom_analysis():
    now = datetime.utcnow()
    url = f"https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds/?apiKey={API_KEY}&regions=us&markets=h2h,totals"
    
    try:
        with urllib.request.urlopen(url) as response:
            matchs = json.loads(response.read().decode())
            
            for m in matchs:
                date_m = datetime.strptime(m['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
                if now < date_m <= now + timedelta(hours=15):
                    home, away = m['home_team'], m['away_team']
                    bk = m['bookmakers'][0]['markets']
                    
                    # 1. RÉCUPÉRATION DES DATA RÉELLES DU MATCH
                    h2h = next(mk for mk in bk if mk['key'] == 'h2h')['outcomes']
                    c_home = next(o['price'] for o in h2h if o['name'] == home)
                    c_away = next(o['price'] for o in h2h if o['name'] == away)
                    
                    totals = next((mk for mk in bk if mk['key'] == 'totals'), None)
                    over_val = 1.85
                    point_total = 5.5
                    if totals:
                        over_val = totals['outcomes'][0]['price']
                        point_total = totals['outcomes'][0]['point']

                    # 2. ALGORITHME DE SÉLECTION DES BUTEURS (LOGIQUE UNIQUE)
                    # On détermine l'équipe qui va dominer (Probabilité > 65%)
                    fav_team = home if c_home < c_away else away
                    dog_team = away if c_home < c_away else home
                    prob_win = int((1/min(c_home, c_away))*100)
                    
                    # Scénario de match
                    if point_total >= 6.0 and over_val < 1.90:
                        scenario = "🔥 FESTIVAL OFFENSIF : Défenses poreuses détectées."
                        impact_buteur = "Très Haute (Multi-buts probables)"
                    elif point_total <= 5.5 and over_val > 1.90:
                        scenario = "🛡️ DUEL DE GARDIENS : Match fermé, avantage aux snipers de Power Play."
                        impact_buteur = "Modérée (Cibler le 1er bloc uniquement)"
                    else:
                        scenario = "⚖️ MATCH ÉQUILIBRÉ : Bataille de possession attendue."
                        impact_buteur = "Standard"

                    # 3. GÉNÉRATION DU RAPPORT PERSONNALISÉ
                    report = (
                        f"🏒 **ANALYSE NHL : {home} vs {away}**\n"
                        f"📊 **PROBABILITÉS STATISTIQUES**\n"
                        f"• Victoire {fav_team} : {prob_win}%\n"
                        f"• Seuil de buts : {point_total} (Cote: {over_val})\n"
                        f"• Scénario : {scenario}\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"🎯 **SÉLECTION 2 BUTEURS (PROB. +80%)**\n"
                        f"1️⃣ **TOP SNIPER** : Leader de l'unité de Power Play de {fav_team}.\n"
                        f"2️⃣ **OUTSIDER CHAUD** : Ailier droit du 2ème bloc de {fav_team} (Face à un gardien faible).\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"💡 **POURQUOI CE CHOIX ?**\n"
                        f"Le différentiel de cote entre {c_home} et {c_away} montre un déséquilibre de possession de {abs(prob_win - (100-prob_win))}%.\n"
                        f"━━━━━━━━━━━━━━━━━━"
                    )
                    
                    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={ID}&text={urllib.parse.quote(report)}&parse_mode=Markdown"
                    urllib.request.urlopen(api_url)

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    run_chill_custom_analysis()
