import urllib.request
import ssl
import feedparser

# Diccionario completo de fuentes RSS sincronizadas
FEEDS = {
    # 1. NÚCLEO INSTITUCIONAL, BOE Y BOD
    "BOE - Búsqueda Directa ISFAS": "https://news.google.com/rss/search?q=site%3Aboe.es+ISFAS&hl=es&gl=ES&ceid=ES:es",
    "BOE - Mutualidades y ISFAS": "https://news.google.com/rss/search?q=site%3Aboe.es+ISFAS+MUFACE&hl=es&gl=ES&ceid=ES:es",
    "ISFAS Sistema Nacional de Salud": "https://news.google.com/rss/search?q=ISFAS+%22Sistema+Nacional+de+Salud%22&hl=es&gl=ES&ceid=ES:es",
    "ISFAS MUFACE MUGEJU": "https://news.google.com/rss/search?q=ISFAS+MUFACE+MUGEJU&hl=es&gl=ES&ceid=ES:es",
    "Boletin Oficial de Defensa BOD": "https://news.google.com/rss/search?q=BOD+%22Boletin+Oficial+de+Defensa%22+site%3Adefensa.gob.es&hl=es&gl=ES&ceid=ES:es",
    "Resoluciones e Instrucciones ISFAS": "https://news.google.com/rss/search?q=ISFAS+BOE+resolucion+instruccion&hl=es&gl=ES&ceid=ES:es",
    "Delegaciones ISFAS": "https://news.google.com/rss/search?q=%22delegacion+del+ISFAS%22&hl=es&gl=ES&ceid=ES:es",
    "ISFAS Instituto Social de las Fuerzas Armadas": "https://news.google.com/rss/search?q=ISFAS+%22Instituto+Social+de+las+Fuerzas+Armadas%22+MUFACE&hl=es&gl=ES&ceid=ES:es",

    # 2. FUENTES DIRECTAS E INSTITUCIONALES
    "Notas de Prensa ISFAS": "https://www.defensa.gob.es/isfas/gabinete/notas_prensa/rss.xml",
    "Gaceta Médica": "https://gacetamedica.com/feed/",
    "Noticias de Diario Médico": "https://www.diariomedico.com/feed",
    "Redacción Médica": "https://redaccionmedica.com/rss/ultimas-noticias.xml",

    # 3. CONCIERTOS, FARMACIA Y RECETA ELECTRÓNICA
    "Concierto Sanitario y Cuadro Médico": "https://news.google.com/rss/search?q=ISFAS+%22concierto+sanitario%22+Adeslas+Asisa&hl=es&gl=ES&ceid=ES:es",
    "Convenios y Aseguradoras": "https://news.google.com/rss/search?q=ISFAS+convenio+concierto+asisa+adeslas&hl=es&gl=ES&ceid=ES:es",
    "Receta Electrónica Avanzada": "https://news.google.com/rss/search?q=ISFAS+%22receta+electronica%22+farmacia&hl=es&gl=ES&ceid=ES:es",
    "Receta Electrónica Mutualidades": "https://news.google.com/rss/search?q=%22receta+electronica%22+ISFAS+MUFACE+MUGEJU&hl=es&gl=ES&ceid=ES:es",
    "Sanidad Militar Gomez Ulla": "https://news.google.com/rss/search?q=%22Sanidad+Militar%22+ISFAS+%22Gomez+Ulla%22&hl=es&gl=ES&ceid=ES:es",

    # 4. PRESTACIONES SOCIALES Y DEPENDENCIA
    "Dependencia y Ayudas ISFAS": "https://news.google.com/rss/search?q=ISFAS+%22prestacion+economica%22+%22ayuda+de+dependencia%22&hl=es&gl=ES&ceid=ES:es",
    "Prestaciones Mutuas": "https://news.google.com/rss/search?q=prestaciones+ISFAS+MUFACE+MUGEJU&hl=es&gl=ES&ceid=ES:es",

    # 5. ASOCIACIONES Y SINDICATOS
    "CSIF e ISFAS": "https://news.google.com/rss/search?q=CSIF+ISFAS+%22Sanidad+Militar%22&hl=es&gl=ES&ceid=ES:es",
    "COPERFAS e ISFAS": "https://news.google.com/rss/search?q=COPERFAS+ISFAS&hl=es&gl=ES&ceid=ES:es",
    "Asociaciones Militares (ASFASPRO AUME ATME)": "https://news.google.com/rss/search?q=ISFAS+ASFASPRO+ATME+AUME&hl=es&gl=ES&ceid=ES:es",

    # 6. PRENSA NACIONAL
    "ABC - ISFAS y Mutualidades": "https://news.google.com/rss/search?q=site%3Aabc.es+ISFAS+MUFACE&hl=es&gl=ES&ceid=ES:es",
    "El País - ISFAS y Sanidad": "https://news.google.com/rss/search?q=site%3Aelpais.com+ISFAS+sanidad&hl=es&gl=ES&ceid=ES:es",
    "El Mundo - Mutualidades Defensa": "https://news.google.com/rss/search?q=site%3Aelmundo.es+ISFAS+MUFACE&hl=es&gl=ES&ceid=ES:es",
    "La Razón - ISFAS Militar": "https://news.google.com/rss/search?q=site%3aklarazon.es+ISFAS+militar&hl=es&gl=ES&ceid=ES:es",
    "Europa Press - ISFAS Actualidad": "https://news.google.com/rss/search?q=site%3Aeuropapress.es+ISFAS+MUFACE&hl=es&gl=ES&ceid=ES:es",

    # 7. PRENSA PROVINCIAL Y REGIONAL
    "La Voz de Galicia - ISFAS": "https://news.google.com/rss/search?q=site%3alavozdegalicia.es+ISFAS+MUFACE&hl=es&gl=ES&ceid=ES:es",
    "El Periódico de Aragón - ISFAS": "https://news.google.com/rss/search?q=site%3aelperiodicodearagon.com+ISFAS&hl=es&gl=ES&ceid=ES:es",
    "La Verdad de Murcia - ISFAS": "https://news.google.com/rss/search?q=site%3alaverdad.es+ISFAS+MUFACE&hl=es&gl=ES&ceid=ES:es",
    "Ideal Andalucía - ISFAS": "https://news.google.com/rss/search?q=site%3aiideal.es+ISFAS+militar&hl=es&gl=ES&ceid=ES:es",
    "El Diario Montañés - ISFAS": "https://news.google.com/rss/search?q=site%3aeldiariomontanes.es+ISFAS&hl=es&gl=ES&ceid=ES:es",
    "Heraldo de Aragón - ISFAS": "https://news.google.com/rss/search?q=site%3aheraldo.es+ISFAS+sanidad&hl=es&gl=ES&ceid=ES:es",
    "Las Provincias (Valencia) - ISFAS": "https://news.google.com/rss/search?q=site%3alasprovincias.es+ISFAS+MUFACE&hl=es&gl=ES&ceid=ES:es"
}

def obtener_noticias():
    noticias_capturadas = []
    
    # Configuración de seguridad SSL flexible para evitar fallos de certificados locales
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Cabecera User-Agent para simular un navegador real y evitar bloqueos en GitHub Actions
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    print("⏳ Descargando noticias desde los RSS con cabeceras de navegador...")

    for categoria, url in FEEDS.items():
        try:
            req = urllib.request.Request(url, headers=headers)
            # Timeout fijado en 10 segundos para agilizar ejecuciones y evitar bloqueos largos
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                html_bytes = response.read()
                feed = feedparser.parse(html_bytes)
                
                for entry in feed.entries:
                    noticias_capturadas.append({
                        'categoria': categoria,
                        'titulo': getattr(entry, 'title', 'Sin título'),
                        'enlace': getattr(entry, 'link', '#'),
                        'fecha': getattr(entry, 'published', 'Fecha no disponible')
                    })
        except Exception as e:
            print(f"⚠️ Nota: No se pudo conectar a {categoria} ({e})")

    return noticias_capturadas

def main():
    noticias = obtener_noticias()
    # Continúa aquí con el resto de la lógica de tu script (generación de HTML, etc.)
    print(f"Total de noticias procesadas: {len(noticias)}")

if __name__ == "__main__":
    main()
