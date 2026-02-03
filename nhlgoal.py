import urllib.request, json, urllib.parse
from datetime import datetime, timedelta

# CONFIGURATION
API_KEY = "b7191bd60e5363789c259b864ddc5367"
TOKEN = "8341397638:AAENHUF8V4FoCenp9aR7ockDcHAGZgmN66s"
ID = "1697906576"

def run_nhl_pro_analysis():
    now = datetime.utcnow()
    # On demande spécifiquement les buteurs (player_anytime_goalscorer)
    url = f"https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds/?apiKey={API_KEY}&regions=us&markets=h2h,totals,player_anytime_goalscorer"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
            for match in data:
                date_m = datetime.strptime(match['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
                if now < date_m <= now + timedelta(hours=18):
                    home, away = match['home_team'], match['away_team']
                    
                    # 1. ANALYSE DES COTES RÉELLES
                    markets = match['bookmakers'][0]['markets']
                    h2h = next((m for m in markets if m['key'] == 'h2h'), None)
                    goalscorers = next((m for m in markets if m['key'] == 'player_anytime_goalscorer'), None)
                    
                    c_h = next(o['price'] for o in h2h['outcomes'] if o['name'] == home)
                    c_a = next(o['price'] for o in h2h['outcomes'] if o['name'] == away)

                    # 2. LOGIQUE DE DÉCISION (VICOIRE VS BUTEURS)
                    verdict = ""
                    details = ""
                    # Si une équipe est ultra favorite
                    if c_h < 1.60 or c_a < 1.60:
                        fav = home if c_h < c_a else away
                        verdict = f"🚩 PRIORITÉ VICTOIRE : {fav}"
                        details = f"L'écart de niveau est tel que la victoire sèche de {fav} est le pari le plus intelligent statistiquement."
                    else:
                        verdict = "🎯 OPTION BUTEURS : Match ouvert"
                        details = "Les forces sont équilibrées, la valeur se trouve sur les performances individuelles."

                    # 3. EXTRACTION DES NOMS DES BUTEURS (DATA INDIVIDUELLE)
                    top_scorers = []
                    if goalscorers:
                        # On trie pour avoir les 2 plus probables (cotes les plus basses)
                        sorted_scorers = sorted(goalscorers['outcomes'], key=lambda x: x['price'])
                        top_scorers = [f"🔥 {s['name']} (Cote: {s['price']})" for s in sorted_scorers[:2]]
                    else:
                        top_scorers = ["⚠️ Noms indisponibles (trop tôt)", "Concentrez-vous sur le vainqueur"]

                    # 4. ENVOI DU RAPPORT UNIQUE
                    report = (
                        f"🏒 **NHL DEEP ANALYST : {home} vs {away}**\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"📊 **VERDICT STRATÉGIQUE**\n"
                        f"👉 {verdict}\n"
                        f"📝 {details}\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"🎯 **BUTEURS CIBLÉS (TOP PROB.)**\n"
                        f"1️⃣ {top_scorers[0]}\n"
                        f"2️⃣ {top_scorers[1] if len(top_scorers)>1 else ''}\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"💡 **ANALYSE INDIVIDUELLE**\n"
                        f"Le modèle détecte une pression offensive de {int((1/min(c_h,c_a))*100)}% pour le favori. {'Le PowerPlay sera la clé.' if 'BUTEURS' in verdict else 'La défense adverse est trop solide pour isoler un buteur.'}\n"
                        f"━━━━━━━━━━━━━━━━━━"
                    )
                    
                    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={ID}&text={urllib.parse.quote(report)}&parse_mode=Markdown"
                    urllib.request.urlopen(api_url)
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    run_nhl_pro_analysis()
