import os
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

# ================= CONFIGURATION CONFIGURABLE =================
# RECOMMANDATION : Remplace "VOTRE_PSEUDO" par ton vrai nom d'utilisateur GitHub
USER_GITHUB = "fetch_news.py"       
NOM_DEPOT = "Trending-News"     
SITE_URL = f"https://{USER_GITHUB}.github.io/{NOM_DEPOT}/"
# ==============================================================

def clean_html(raw_html):
    """Supprime proprement les balises HTML des descriptions pour le résumé."""
    if not raw_html:
        return "Aucun résumé disponible."
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext[:180] + "..." if len(cleantext) > 180 else cleantext

def generate_seo_files():
    """Génère les fichiers indispensables pour forcer l'indexation Google."""
    print("Génération automatique des fichiers SEO (robots.txt et sitemap.xml)...")
    
    # 1. robots.txt
    robots_content = f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml"
    with open("robots.txt", "w", encoding="utf-8") as f:
        f.write(robots_content)
        
    # 2. sitemap.xml
    aujourdhui = datetime.now().strftime("%Y-%m-%d")
    sitemap_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '  <url>\n'
        '    <loc>' + SITE_URL + '</loc>\n'
        '    <lastmod>' + aujourdhui + '</lastmod>\n'
        '    <changefreq>hourly</changefreq>\n'
        '    <priority>1.0</priority>\n'
        '  </url>\n'
        '</urlset>'
    )
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_content)

def fetch_trending_news():
    print("Connexion au flux de Trending News...")
    # Requête de recherche sur les actualités Tech et Finance en Français
    url = "https://news.google.com/rss/search?q=technology+finance&hl=fr&gl=FR&ceid=FR:fr"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        articles = []
        
        # Collecte des 15 articles les plus récents
        for item in root.findall('.//item')[:15]:
            title = item.find('title').text if item.find('title') is not None else "Sans titre"
            link = item.find('link').text if item.find('link') is not None else "#"
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
            description = item.find('description').text if item.find('description') is not None else ""
            
            clean_title = title
            source = "Trending News Media"
            if " - " in title:
                clean_title = " - ".join(title.split(" - ")[:-1])
                source = title.split(" - ")[-1]

            try:
                # Extraction et conversion de la date de publication au format standardisé
                date_obj = datetime.strptime(pub_date[:25], "%a, %d %b %Y %H:%M:%S")
                date_iso = date_obj.isoformat()
                date_format = date_obj.strftime("%d/%m à %H:%M")
            except:
                date_iso = datetime.now().isoformat()
                date_format = pub_date

            articles.append({
                "title": clean_title,
                "url": link,
                "source": source,
                "date": date_format,
                "date_iso": date_iso,
                "summary": clean_html(description)
            })
            
        # Création du dossier data s'il n'existe pas
        os.makedirs("data", exist_ok=True)
        maintenant = datetime.now().strftime("%d/%m/%Y à %H:%M")
        
        output_data = {
            "last_updated": maintenant,
            "articles": articles
        }
        
        # Sauvegarde propre du fichier de données
        with open("data/latest_news.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
            
        # Lancement de l'écriture des fichiers SEO
        generate_seo_files()
        print(f"Succès total. {len(articles)} articles synchronisés.")
        
    except Exception as e:
        print(f"Une erreur est survenue lors de l'exécution : {e}")
        raise e

if __name__ == "__main__":
    fetch_trending_news()

