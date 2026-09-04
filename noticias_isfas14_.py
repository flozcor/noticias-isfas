# noticias_isfas14.py
# v20.7 - Historial persistente, diseño integrado y copia optimizada a ancho completo (100%) para Outlook

import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

# ARCHIVO DE HISTORIAL LOCAL
HISTORIAL_FILE = "historial_enviadas.json"

def cargar_historial_json():
    if os.path.exists(HISTORIAL_FILE):
        try:
            with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def guardar_historial_json(enlaces):
    enviadas = cargar_historial_json()
    for enlace in enlaces:
        enviadas.add(enlace)
    try:
        with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
            json.dump(list(enviadas), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Error al guardar el archivo de historial: {e}")

# DICCIONARIO DE FUENTES RSS COMPLETO (Sincronizado con Inoreader y OPML)
FEEDS = {
    # 1. NÚCLEO INSTITUCIONAL, BOE Y BOD
    'BOE - Búsqueda Directa ISFAS': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('site:boe.es ISFAS') + '&hl=es&gl=ES&ceid=ES:es',
    'BOE - Mutualidades y ISFAS': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('site:boe.es ISFAS MUFACE') + '&hl=es&gl=ES&ceid=ES:es',
    'ISFAS Sistema Nacional de Salud': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('ISFAS "Sistema Nacional de Salud"') + '&hl=es&gl=ES&ceid=ES:es',
    'ISFAS MUFACE MUGEJU': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('ISFAS MUFACE MUGEJU') + '&hl=es&gl=ES&ceid=ES:es',
    'Boletin Oficial de Defensa BOD': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('BOD "Boletin Oficial de Defensa" site:defensa.gob.es') + '&hl=es&gl=ES&ceid=ES:es',
    'Resoluciones e Instrucciones ISFAS': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('ISFAS BOE resolucion instruccion') + '&hl=es&gl=ES&ceid=ES:es',
    'Delegaciones ISFAS': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('"delegacion del ISFAS"') + '&hl=es&gl=ES&ceid=ES:es',
    'ISFAS Instituto Social de las Fuerzas Armadas': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('ISFAS "Instituto Social de las Fuerzas Armadas" MUFACE') + '&hl=es&gl=ES&ceid=ES:es',

    # 2. FUENTES DIRECTAS E INSTITUCIONALES
    'Notas de Prensa ISFAS': 'https://www.defensa.gob.es/isfas/gabinete/notas_prensa/rss.xml',
    'Gaceta Médica': 'https://gacetamedica.com/feed/',
    'Noticias de Diario Médico': 'https://www.diariomedico.com/feed',
    'Redacción Médica': 'https://redaccionmedica.com/rss/ultimas-noticias.xml',

    # 3. CONCIERTOS, FARMACIA Y RECETA ELECTRÓNICA
    'Concierto Sanitario y Cuadro Médico': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('ISFAS "concierto sanitario" Adeslas Asisa') + '&hl=es&gl=ES&ceid=ES:es',
    'Convenios y Aseguradoras': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('ISFAS convenio concierto asisa adeslas') + '&hl=es&gl=ES&ceid=ES:es',
    'Receta Electrónica Avanzada': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('ISFAS "receta electronica" farmacia') + '&hl=es&gl=ES&ceid=ES:es',
    'Receta Electrónica Mutualidades': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('"receta electronica" ISFAS MUFACE MUGEJU') + '&hl=es&gl=ES&ceid=ES:es',
    'Sanidad Militar Gomez Ulla': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('"Sanidad Militar" ISFAS "Gomez Ulla"') + '&hl=es&gl=ES&ceid=ES:es',

    # 4. PRESTACIONES SOCIALES Y DEPENDENCIA
    'Dependencia y Ayudas ISFAS': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('ISFAS "prestacion economica" "ayuda de dependencia"') + '&hl=es&gl=ES&ceid=ES:es',
    'Prestaciones Mutuas': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('prestaciones ISFAS MUFACE MUGEJU') + '&hl=es&gl=ES&ceid=ES:es',

    # 5. ASOCIACIONES Y SINDICATOS
    'CSIF e ISFAS': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('CSIF ISFAS "Sanidad Militar"') + '&hl=es&gl=ES&ceid=ES:es',
    'COPERFAS e ISFAS': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('COPERFAS ISFAS') + '&hl=es&gl=ES&ceid=ES:es',
    'Asociaciones Militares': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('ISFAS ASFASPRO ATME AUME') + '&hl=es&gl=ES&ceid=ES:es',

    # 6. PRENSA NACIONAL
    'ABC - ISFAS y Mutualidades': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('site:abc.es ISFAS MUFACE') + '&hl=es&gl=ES&ceid=ES:es',
    'El País - ISFAS y Sanidad': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('site:elpais.com ISFAS sanidad') + '&hl=es&gl=ES&ceid=ES:es',
    'El Mundo - Mutualidades Defensa': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('site:elmundo.es ISFAS MUFACE') + '&hl=es&gl=ES&ceid=ES:es',
    'La Razón - ISFAS Militar': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('site:larazon.es ISFAS militar') + '&hl=es&gl=ES&ceid=ES:es',
    'Europa Press - ISFAS Actualidad': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('site:europapress.es ISFAS MUFACE') + '&hl=es&gl=ES&ceid=ES:es',

    # 7. PRENSA PROVINCIAL Y REGIONAL
    'La Voz de Galicia - ISFAS': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('site:lavozdegalicia.es ISFAS MUFACE') + '&hl=es&gl=ES&ceid=ES:es',
    'El Periódico de Aragón - ISFAS': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('site:elperiodicodearagon.com ISFAS') + '&hl=es&gl=ES&ceid=ES:es',
    'La Verdad de Murcia - ISFAS': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('site:laverdad.es ISFAS MUFACE') + '&hl=es&gl=ES&ceid=ES:es',
    'Ideal Andalucía - ISFAS': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('site:ideal.es ISFAS militar') + '&hl=es&gl=ES&ceid=ES:es',
    'El Diario Montañés - ISFAS': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('site:eldiariomontanes.es ISFAS') + '&hl=es&gl=ES&ceid=ES:es',
    'Heraldo de Aragón - ISFAS': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('site:heraldo.es ISFAS sanidad') + '&hl=es&gl=ES&ceid=ES:es',
    'Las Provincias (Valencia) - ISFAS': 'https://news.google.com/rss/search?q=' + urllib.parse.quote('site:lasprovincias.es ISFAS MUFACE') + '&hl=es&gl=ES&ceid=ES:es'
}
MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def obtener_noticias():
    noticias = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    item_id = 1
    for categoria, url in FEEDS.items():
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)

                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else 'Sin título'
                    link = item.find('link').text if item.find('link') is not None else '#'
                    pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ''
                    
                    fuente = "Prensa"
                    if " - " in title:
                        partes = title.rsplit(" - ", 1)
                        title = partes[0]
                        fuente = partes[1]

                    pub_datetime = datetime.now()
                    if pub_date_str:
                        try:
                            pub_datetime = parsedate_to_datetime(pub_date_str)
                        except Exception:
                            pass

                    noticias.append({
                        "id": item_id,
                        "categoria": categoria,
                        "titulo": title,
                        "enlace": link,
                        "fecha_str": pub_datetime.strftime("%d/%m/%Y %H:%M"),
                        "year": pub_datetime.year,
                        "month": pub_datetime.month,
                        "month_name": MESES_ES.get(pub_datetime.month, ""),
                        "day": pub_datetime.day,
                        "date_key": pub_datetime.strftime("%Y-%m-%d"),
                        "fuente": fuente,
                        "timestamp": pub_datetime.timestamp()
                    })
                    item_id += 1
        except Exception as e:
            print(f"⚠️ Nota: No se pudo conectar a {categoria} ({e}).")

    if not noticias:
        ahora = datetime.now()
        noticias = [{
            "id": 1,
            "categoria": "Hospitales Militares",
            "titulo": "El Cuerpo Militar de Sanidad refuerza los contingentes de apoyo sanitario",
            "enlace": "https://www.defensa.gob.es",
            "fecha_str": ahora.strftime("%d/%m/%Y %H:%M"),
            "year": ahora.year,
            "month": ahora.month,
            "month_name": MESES_ES.get(ahora.month, ""),
            "day": ahora.day,
            "date_key": ahora.strftime("%Y-%m-%d"),
            "fuente": "Ministerio de Defensa",
            "timestamp": ahora.timestamp()
        }]

    noticias.sort(key=lambda x: x['timestamp'], reverse=True)
    return noticias

def generar_html_interactivo(noticias):
    noticias_json = json.dumps(noticias, ensure_ascii=False)
    enviadas_set = cargar_historial_json()
    enviadas_json = json.dumps(list(enviadas_set), ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ISFAS - Gestor de Noticias</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-blue: #2c5282; 
            --accent-blue: #3182ce;
            --text-color: #2d3748;
            --bg-body: #f7fafc;
        }}

        body {{
            font-family: 'Montserrat', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            background-color: var(--bg-body);
            color: var(--text-color);
        }}

        header {{
            background: linear-gradient(135deg, #1a365d 0%, var(--primary-blue) 100%);
            color: #ffffff;
            padding: 40px 20px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border-bottom: 4px solid var(--accent-blue);
        }}

        header h1 {{
            margin: 0;
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}

        header .subtitulo {{
            margin-top: 8px;
            font-size: 1rem;
            font-weight: 400;
            color: #e2e8f0;
            letter-spacing: 1px;
        }}

        header .fecha-badge {{
            display: inline-block;
            margin-top: 15px;
            background-color: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(5px);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        main {{
            flex: 1;
            padding: 30px;
            max-width: 1100px;
            margin: 20px auto;
            width: 100%;
            box-sizing: border-box;
        }}

        .controls {{
            background: #ffffff;
            padding: 18px 24px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 25px;
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
            border: 1px solid #e2e8f0;
        }}

        label {{ font-weight: 600; font-size: 0.9rem; }}
        select, button {{
            padding: 9px 14px;
            border-radius: 6px;
            border: 1px solid #cbd5e1;
            font-size: 0.9rem;
            font-family: inherit;
        }}
        
        button {{
            background-color: #2c5282;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.2s;
        }}
        button:hover {{ background-color: #1a365d; }}

        .btn-secondary {{
            background-color: var(--accent-blue);
        }}
        .btn-secondary:hover {{ background-color: var(--primary-blue); }}

        .btn-success {{
            background-color: #2f855a;
        }}
        .btn-success:hover {{ background-color: #276749; }}

        .card {{
            padding: 16px 20px;
            margin-bottom: 12px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            display: flex;
            align-items: flex-start;
            gap: 15px;
        }}

        .card-content {{ flex-grow: 1; }}
        
        .badge {{
            font-size: 11px;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 4px;
            background: #ebf8ff;
            color: #2b6cb0;
            text-transform: uppercase;
        }}

        .title {{ font-size: 1.05rem; font-weight: 600; margin: 8px 0; line-height: 1.4; }}
        .title a {{ color: #2d3748; text-decoration: none; }}
        .title a:hover {{ color: var(--accent-blue); text-decoration: underline; }}
        .meta {{ font-size: 0.82rem; color: #718096; }}

        .checkbox-container {{ padding-top: 4px; }}
        input[type="checkbox"] {{ transform: scale(1.3); cursor: pointer; }}

        footer {{
            background-color: var(--primary-blue);
            color: #ffffff;
            text-align: center;
            padding: 20px;
            font-size: 0.95rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
            line-height: 1.5;
        }}
        footer span {{ color: #cbd5e0; font-weight: 400; display: block; font-size: 0.85rem; margin-top: 4px; }}
    </style>
</head>
<body>

    <header>
        <h1>ISFAS</h1>
        <div class="subtitulo">OFICINA DE COMUNICACIÓN</div>
        <div class="fecha-badge" id="fecha-actual"></div>
    </header>

    <main>
        <div class="controls">
            <div>
                <label for="dateSelect">📅 Filtrar Fecha:</label>
                <select id="dateSelect" onchange="filtrarNoticias()">
                    <option value="TODOS">-- Mostrar Todas --</option>
                </select>
            </div>
            <div>
                <button class="btn-secondary" onclick="marcarTodas(true)">Seleccionar Visibles</button>
                <button class="btn-secondary" onclick="marcarTodas(false)">Desmarcar</button>
            </div>
            <div style="margin-left: auto; display: flex; gap: 10px;">
                <button class="btn-success" onclick="copiarParaEmail()">📋 Copiar para Email</button>
                <button onclick="exportarSeleccionadas()">📥 Exportar Informe HTML</button>
            </div>
        </div>

        <div id="newsContainer"></div>
    </main>

    <footer>
        @ISFAS - Instituto Social de las Fuerzas Armadas
        <span>Oficina de Comunicación - Capitán de Corbeta Fran Lozano</span>
    </footer>

    <script>
        const dataset = {noticias_json};
        let enviadasSet = new Set({enviadas_json});

        function cargarFechaEncabezado() {{
            const opciones = {{ weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }};
            const hoy = new Date();
            let fechaTexto = hoy.toLocaleDateString('es-ES', opciones);
            fechaTexto = fechaTexto.charAt(0).toUpperCase() + fechaTexto.slice(1);
            document.getElementById('fecha-actual').textContent = fechaTexto;
        }}

        function poblarDesplegable() {{
            const select = document.getElementById('dateSelect');
            const arbol = {{}};

            dataset.forEach(item => {{
                if (!arbol[item.year]) arbol[item.year] = {{}};
                if (!arbol[item.year][item.month]) arbol[item.year][item.month] = {{
                    nombre: item.month_name,
                    dias: {{}}
                }};
                if (!arbol[item.year][item.month].dias[item.day]) {{
                    arbol[item.year][item.month].dias[item.day] = item.date_key;
                }}
            }});

            Object.keys(arbol).sort((a,b) => b - a).forEach(year => {{
                Object.keys(arbol[year]).sort((a,b) => b - a).forEach(month => {{
                    const mesInfo = arbol[year][month];
                    Object.keys(mesInfo.dias).sort((a,b) => b - a).forEach(day => {{
                        const dateKey = mesInfo.dias[day];
                        const option = document.createElement('option');
                        option.value = dateKey;
                        option.textContent = `${{year}} > ${{mesInfo.nombre}} > Día ${{day.padStart(2, '0')}}`;
                        select.appendChild(option);
                    }});
                }});
            }});
        }}

        function renderizar(lista) {{
            const container = document.getElementById('newsContainer');

            if (lista.length === 0) {{
                container.innerHTML = '<p style="text-align:center; padding: 40px; color: #718096;">No hay noticias disponibles para el filtro seleccionado.</p>';
                return;
            }}

            container.innerHTML = lista.map(item => {{
                const yaEnviada = enviadasSet.has(item.enlace);
                
                const cardStyle = yaEnviada 
                    ? 'background: #fde8e8; border-left: 5px solid #e53e3e; border-top: 1px solid #fbd5d5; border-right: 1px solid #fbd5d5; border-bottom: 1px solid #fbd5d5;' 
                    : 'background: #ffffff; border-left: 5px solid var(--accent-blue); border-top: 1px solid #edf2f7; border-right: 1px solid #edf2f7; border-bottom: 1px solid #edf2f7;';
                
                const badgeEnviada = yaEnviada 
                    ? '<span style="font-size: 10px; font-weight: 700; padding: 3px 6px; border-radius: 4px; background: #e53e3e; color: #ffffff; margin-left: 8px; text-transform: uppercase;">📤 Ya enviada</span>' 
                    : '';

                return `
                    <div class="card" style="${{cardStyle}}">
                        <div class="checkbox-container">
                            <input type="checkbox" class="chk-export" data-id="${{item.id}}" data-enlace="${{item.enlace}}">
                        </div>
                        <div class="card-content">
                            <div>
                                <span class="badge">${{item.categoria}}</span>
                                ${{badgeEnviada}}
                                <span class="meta" style="float:right;">🕒 ${{item.fecha_str}}</span>
                            </div>
                            <div class="title">
                                <a href="${{item.enlace}}" target="_blank">${{item.titulo}}</a>
                            </div>
                            <div class="meta">📍 Fuente: <strong>${{item.fuente}}</strong></div>
                        </div>
                    </div>
                `;
            }}).join('');
        }}

        function filtrarNoticias() {{
            const val = document.getElementById('dateSelect').value;
            if (val === 'TODOS') {{
                renderizar(dataset);
            }} else {{
                const filtradas = dataset.filter(item => item.date_key === val);
                renderizar(filtradas);
            }}
        }}

        function marcarTodas(estado) {{
            document.querySelectorAll('.chk-export').forEach(chk => chk.checked = estado);
        }}

        function copiarParaEmail() {{
            const seleccionadosIds = Array.from(document.querySelectorAll('.chk-export:checked'))
                .map(chk => parseInt(chk.getAttribute('data-id')));

            if (seleccionadosIds.length === 0) {{
                alert('Por favor, selecciona al menos una noticia para copiar al portapapeles.');
                return;
            }}

            const seleccionados = dataset.filter(item => seleccionadosIds.includes(item.id));
            const enlacesSeleccionados = seleccionados.map(item => item.enlace);

            actualizarHistorialServidor(enlacesSeleccionados);

            const hoy = new Date();
            const opciones = {{ weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }};
            let fechaTexto = hoy.toLocaleDateString('es-ES', opciones);
            fechaTexto = fechaTexto.charAt(0).toUpperCase() + fechaTexto.slice(1);

            // --- HTML FLUIDO AL 100% DE ANCHO (Estilo Web a pantalla completa) ---
            let htmlSnippet = '<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f7fafc; font-family: Arial, sans-serif;">';
            htmlSnippet += '<tr><td align="center" style="padding: 0;">';
            
            htmlSnippet += '<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0;">';
            
            // 1. ENCABEZADO CORPORATIVO EXTENDIDO AL 100%
            htmlSnippet += '<tr><td align="center" style="background-color: #1a365d; padding: 30px 20px; color: #ffffff;">';
            htmlSnippet += '<table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center">';
            htmlSnippet += '<h1 style="margin: 0; font-size: 24px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase; color: #ffffff;">ISFAS</h1>';
            htmlSnippet += '<div style="margin-top: 5px; font-size: 13px; color: #e2e8f0; letter-spacing: 1px;">OFICINA DE COMUNICACIÓN</div>';
            htmlSnippet += '<table border="0" cellspacing="0" cellpadding="0" style="margin-top: 12px;"><tr><td align="center" bgcolor="#2c5282" style="padding: 6px 18px; border-radius: 12px; font-size: 12px; color: #ffffff; font-weight: bold;">' + fechaTexto + '</td></tr></table>';
            htmlSnippet += '</td></tr></table>';
            htmlSnippet += '</td></tr>';

            // 2. CUERPO DE NOTICIAS (Con espaciado fluido)
            htmlSnippet += '<tr><td style="padding: 30px 40px;">';

            let textSnippet = "";

            seleccionados.forEach(item => {{
                enviadasSet.add(item.enlace);

                htmlSnippet += '<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-left: 4px solid #3182ce; border-top: 1px solid #edf2f7; border-right: 1px solid #edf2f7; border-bottom: 1px solid #edf2f7; margin-bottom: 15px; border-radius: 6px;">';
                htmlSnippet += '<tr><td style="padding: 18px;">';
                
                htmlSnippet += '<table width="100%" cellpadding="0" cellspacing="0" border="0"><tr>';
                htmlSnippet += '<td><span style="font-size: 10px; font-weight: bold; padding: 3px 8px; background-color: #ebf8ff; color: #2b6cb0; text-transform: uppercase;">' + item.categoria + '</span></td>';
                htmlSnippet += '<td align="right" style="font-size: 11px; color: #718096;">🕒 ' + item.fecha_str + '</td>';
                htmlSnippet += '</tr></table>';

                htmlSnippet += '<div style="font-size: 16px; font-weight: bold; margin: 10px 0 6px 0; line-height: 1.4;">';
                htmlSnippet += '<a href="' + item.enlace + '" target="_blank" style="color: #2d3748; text-decoration: none;">' + item.titulo + '</a>';
                htmlSnippet += '</div>';

                htmlSnippet += '<div style="font-size: 11px; color: #718096;">📍 Fuente: <strong>' + item.fuente + '</strong></div>';
                
                htmlSnippet += '</td></tr></table>';

                textSnippet += '[' + item.categoria + '] ' + item.titulo + '\\nEnlace: ' + item.enlace + '\\nFecha: ' + item.fecha_str + ' | Fuente: ' + item.fuente + '\\n\\n';
            }});

            htmlSnippet += '</td></tr>';

            // 3. PIE DE PÁGINA EXTENDIDO AL 100%
            htmlSnippet += '<tr><td align="center" style="background-color: #2c5282; color: #ffffff; padding: 20px; font-size: 13px; font-weight: bold; line-height: 1.4;">';
            htmlSnippet += '@ISFAS - Instituto Social de las Fuerzas Armadas';
            htmlSnippet += '<div style="color: #cbd5e0; font-weight: normal; font-size: 11px; margin-top: 4px;">Oficina de Comunicación - Capitán de Corbeta Fran Lozano</div>';
            htmlSnippet += '</td></tr>';

            htmlSnippet += '</table>';
            htmlSnippet += '</td></tr></table>';

            filtrarNoticias();

            if (navigator.clipboard && window.ClipboardItem) {{
                const blobHtml = new Blob([htmlSnippet], {{ type: 'text/html' }});
                const blobText = new Blob([textSnippet], {{ type: 'text/plain' }});
                const data = [new ClipboardItem({{ 'text/html': blobHtml, 'text/plain': blobText }})];
                navigator.clipboard.write(data).then(() => {{
                    alert('¡Informe copiado al 100% de ancho con éxito para Outlook!');
                }}).catch(err => {{
                    fallbackCopiarTexto(textSnippet);
                }});
            }} else {{
                fallbackCopiarTexto(textSnippet);
            }}
        }}

        function actualizarHistorialServidor(nuevosEnlaces) {{
            nuevosEnlaces.forEach(e => enviadasSet.add(e));
            const blob = new Blob([JSON.stringify(Array.from(enviadasSet), null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'historial_enviadas.json';
            a.click();
            URL.revokeObjectURL(url);
        }}

        function fallbackCopiarTexto(texto) {{
            const textarea = document.createElement('textarea');
            textarea.value = texto;
            document.body.appendChild(textarea);
            textarea.select();
            try {{
                document.execCommand('copy');
                alert('¡Noticias copiadas y archivo historial_enviadas.json actualizado para descargar!');
            }} catch (err) {{
                alert('No se pudo copiar automáticamente.');
            }}
            document.body.removeChild(textarea);
        }}

        function exportarSeleccionadas() {{
            const seleccionadosIds = Array.from(document.querySelectorAll('.chk-export:checked'))
                .map(chk => parseInt(chk.getAttribute('data-id')));

            if (seleccionadosIds.length === 0) {{
                alert('Por favor, selecciona al menos una noticia para exportar.');
                return;
            }}

            const seleccionados = dataset.filter(item => seleccionadosIds.includes(item.id));
            
            const hoy = new Date();
            const opciones = {{ weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }};
            let fechaFijaTexto = hoy.toLocaleDateString('es-ES', opciones);
            fechaFijaTexto = fechaFijaTexto.charAt(0).toUpperCase() + fechaFijaTexto.slice(1);

            const pad = (n) => String(n).padStart(2, '0');
            const strFechaArchivo = `${{hoy.getFullYear()}}${{pad(hoy.getMonth()+1)}}_${{pad(hoy.getDate())}}_${{pad(hoy.getHours())}}${{pad(hoy.getMinutes())}}${{pad(hoy.getSeconds())}}`;
            const nombreArchivo = `Informe_isfas_${{strFechaArchivo}}.html`;

            const htmlExport = `<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ISFAS - Oficina de Comunicación</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-blue: #2c5282; 
            --accent-blue: #3182ce;
            --text-color: #2d3748;
            --bg-body: #f7fafc;
        }}

        body {{
            font-family: 'Montserrat', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            background-color: var(--bg-body);
            color: var(--text-color);
        }}

        header {{
            background: linear-gradient(135deg, #1a365d 0%, var(--primary-blue) 100%);
            color: #ffffff;
            padding: 40px 20px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border-bottom: 4px solid var(--accent-blue);
        }}

        header h1 {{
            margin: 0;
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}

        header .subtitulo {{
            margin-top: 8px;
            font-size: 1rem;
            font-weight: 400;
            color: #e2e8f0;
            letter-spacing: 1px;
        }}

        header .fecha-badge {{
            display: inline-block;
            margin-top: 15px;
            background-color: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(5px);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        main {{
            flex: 1;
            padding: 40px 30px;
            max-width: 1000px;
            margin: 30px auto;
            width: 100%;
            box-sizing: border-box;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border: 1px solid #e2e8f0;
        }}

        .card-noticia {{
            border-left: 5px solid var(--accent-blue);
            background: #ffffff;
            padding: 16px 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            border-top: 1px solid #edf2f7;
            border-right: 1px solid #edf2f7;
            border-bottom: 1px solid #edf2f7;
        }}

        .badge-cat {{
            font-size: 11px;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 4px;
            background: #ebf8ff;
            color: #2b6cb0;
            text-transform: uppercase;
        }}

        .titulo-noticia {{
            font-size: 1.1rem;
            font-weight: 600;
            margin: 10px 0 6px 0;
            line-height: 1.4;
        }}

        .titulo-noticia a {{
            color: var(--text-color);
            text-decoration: none;
        }}

        .titulo-noticia a:hover {{
            color: var(--accent-blue);
            text-decoration: underline;
        }}

        .meta-noticia {{
            font-size: 0.85rem;
            color: #718096;
        }}

        footer {{
            background-color: var(--primary-blue);
            color: #ffffff;
            text-align: center;
            padding: 20px;
            font-size: 0.95rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
            line-height: 1.5;
        }}

        footer span {{
            color: #cbd5e0;
            font-weight: 400;
            display: block;
            font-size: 0.85rem;
            margin-top: 4px;
        }}
    </style>
</head>
<body>

    <header>
        <h1>ISFAS</h1>
        <div class="subtitulo">OFICINA DE COMUNICACIÓN</div>
        <div class="fecha-badge" id="fecha-actual">${{fechaFijaTexto}}</div>
    </header>

    <main>
        <h2 style="color: var(--primary-blue); margin-top: 0; margin-bottom: 25px; border-bottom: 2px solid #edf2f7; padding-bottom: 10px;">Informe Oficial de Noticias Seleccionadas</h2>
        
        ${{seleccionados.map(item => `
            <div class="card-noticia">
                <div>
                    <span class="badge-cat">${{item.categoria}}</span>
                    <span class="meta-noticia" style="float: right;">🕒 ${{item.fecha_str}}</span>
                </div>
                <div class="titulo-noticia">
                    <a href="${{item.enlace}}" target="_blank">${{item.titulo}}</a>
                </div>
                <div class="meta-noticia">📍 Fuente: <strong>${{item.fuente}}</strong></div>
            </div>
        `).join('')}}
    </main>

    <footer>
        @ISFAS - Instituto Social de las Fuerzas Armadas
        <span>Oficina de Comunicación - Capitán de Corbeta Fran Lozano</span>
    </footer>

</body>
</html>`;

            const blob = new Blob([htmlExport], {{ type: 'text/html' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = nombreArchivo;
            a.click();
            URL.revokeObjectURL(url);
        }}

        // Inicialización
        cargarFechaEncabezado();
        poblarDesplegable();
        renderizar(dataset);
    </script>
</body>
</html>
"""

def main():
    print("⏳ Descargando noticias desde los RSS de Inoreader...")
    noticias = obtener_noticias()
    
    timestamp_filename = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_filename = f"Informe_Sanidad_Interactivo_{timestamp_filename}.html"
    
    html_content = generar_html_interactivo(noticias)
    
    try:
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(html_content)
            f.flush()
            os.fsync(f.fileno())
        print(f"📄 Archivo HTML generado con éxito: {os.path.abspath(html_filename)}")
    except Exception as e:
        print(f"❌ Error al guardar el archivo: {e}")

if __name__ == "__main__":
