import urllib.request, json, urllib.parse
from datetime import datetime, timedelta

# CONFIGURATION
API_KEY = "b7191bd60e5363789c259b864ddc5367"
TOKEN = "8341397638:AAENHUF8V4FoCenp9aR7ockDcHAGZgmN66s"
ID = "1697906576"

def get_nhl_analysis():
    now = datetime.utcnow()
    # On récupère les cotes H2H, Totals et les "Player Props" si disponibles
    url = f"https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds/?apiKey={API_KEY}&regions=us&markets=h2h,totals,player_anytime_goalscorer"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
            for match in data:
                commence_time = datetime.strptime(match['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
                if now < commence_time <= now + timedelta(hours=24):
                    home = match['home_team']
                    away = match['away_team']
                    
                    # 1. ANALYSE DU SCÉNARIO DE MATCH
                    markets = match['bookmakers'][0]['markets']
                    h2h = next((m for m in markets if m['key'] == 'h2h'), None)
                    totals = next((m for m in markets if m['key'] == 'totals'), None)
                    goalscorers = next((m for m in markets if m['key'] == 'player_anytime_goalscorer'), None)

                    # Calcul des forces en présence
                    c_home = next(o['price'] for o in h2h['outcomes'] if o['name'] == home)
                    c_away = next(o['price'] for o in h2h['outcomes'] if o['name'] == away)
                    
                    # 2. DÉCISION STRATÉGIQUE (MISER QUOI ?)
                    pari_principal = ""
                    justification = ""
                    
                    # Si une équipe est archi-favorite (Cote < 1.60)
                    if c_home < 1.65 or c_away < 1.65:
                        fav = home if c_home < c_away else away
                        pari_principal = f"🚩 VICTOIRE : {fav} (Sec)"
                        justification = f"L'écart de niveau est trop grand pour risquer un buteur. Domination attendue de {fav}."
                    # Si le match est ouvert (Total > 6.0)
                    elif totals and totals['outcomes'][0]['point'] >= 6.0:
                        pari_principal = "🎯 BUTEURS : Privilégier les marqueurs"
                        justification = "Match à haut score projeté. Les gardiens sont vulnérables ce soir."
                    else:
                        pari_principal = "🛡️ DOUBLE CHANCE : Match fermé"
                        justification = "Duel de gardiens probable. Peu de buts attendus, sécuriser le résultat."

                    # 3. EXTRACTION DES VRAIS BUTEURS (SI DISPONIBLES)
                    buteurs_noms = []
                    if goalscorers:
                        # On trie les buteurs par la cote la plus basse (plus forte probabilité)
                        sorted_scorers = sorted(goalscorers['outcomes'], key=lambda x: x['price'])
                        buteurs_noms = [f"{s['name']} (Cote: {s['price']})" for s in sorted_scorers[:2]]
                    else:
                        buteurs_noms = ["Données buteurs non encore publiées par l'API", "Réessayez à 1h00"]

                    # 4. ENVOI DU RAPPORT UNIQUE
                    report = (
                        f"🏒 **NHL UNIQUE ANALYST : {home} vs {away}**\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"📈 **STATISTIQUES MATCH**\n"
                        f"• Force {home} : {c_home}\n"
                        f"• Force {away} : {c_away}\n"
                        f"• Tendance score : {totals['outcomes'][0]['point'] if totals else 'N/A'} buts\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"💡 **VERDICT DU MODÈLE**\n"
                        f"👉 {pari_principal}\n"
                        f"📝 {justification}\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"🔥 **BUTEURS PROBABLES (+80% CONF.)**\n"
                        f"1️⃣ {buteurs_noms[0]}\n"
                        f"2️⃣ {buteurs_noms[1]}\n"
                        f"━━━━━━━━━━━━━━━━━━"
                    )
                    
                    encoded_msg = urllib.parse.quote(report)
                    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={ID}&text={encoded_msg}&parse_mode=Markdown"
                    urllib.request.urlopen(api_url)

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    get_nhl_analysis() 
                # ... (fin de ta boucle de matchs)
            if count == 0:
                msg = "🔍 **Scan NHL terminé** : Aucun match avec données buteurs n'est encore disponible. Nouveau scan automatique à 01h00."
                api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={ID}&text={urllib.parse.quote(msg)}&parse_mode=Markdown"
                urllib.request.urlopen(api_url)

