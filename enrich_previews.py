import os
import sys
import json
import re
import urllib.request
import urllib.parse
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON = os.path.join(WORKSPACE_DIR, "canciones_just_dance.json")
OUTPUT_JSON = INPUT_JSON
OUTPUT_JS = os.path.join(WORKSPACE_DIR, "data.js")
CACHE_FILE = os.path.join(WORKSPACE_DIR, "previews_cache.json")

# Artistas de covers de Just Dance / Ubisoft
JUST_DANCE_COVER_ARTISTS = {
    "the just dance band",
    "the sunlight shakers",
    "the hit crew",
    "studio allstars",
    "the countdown singers",
    "top-hat edit",
    "just dance",
    "ubisoft",
    "the franklin electric",
    "the girly team",
    "love potion",
    "the revenge team",
    "halloween thrills",
    "the sunset crew",
    "reggaeton",
    "santa clones",
    "the dancing bros."
}

def clean_title(title):
    t = title
    # Quitar sufijos entre paréntesis o corchetes comunes en Just Dance
    t = re.sub(r'\s*\((just dance|alternate|alternative|vip made|extreme|sweat|classic|fan made|kids|cover).*?\)', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s*\[(just dance|alternate|alternative|vip made|extreme|sweat|classic|fan made|kids|cover).*?\]', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s*-\s*(just dance|alternate|extreme|sweat).*', '', t, flags=re.IGNORECASE)
    # Quitar feat / ft
    t = re.sub(r'\s*\(?(feat\.|ft\.).*?\)?', '', t, flags=re.IGNORECASE)
    return t.strip()

def search_deezer(query):
    url = f"https://api.deezer.com/search?q={urllib.parse.quote(query)}&limit=3"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as res:
            if res.status == 200:
                data = json.loads(res.read().decode('utf-8'))
                items = data.get('data', [])
                for item in items:
                    preview = item.get('preview')
                    if preview:
                        album = item.get('album', {})
                        cover = album.get('cover_medium') or album.get('cover_big') or album.get('cover')
                        return preview, cover, item.get('title')
    except Exception:
        pass
    return None, None, None

def search_itunes(query):
    url = f"https://itunes.apple.com/search?term={urllib.parse.quote(query)}&entity=song&limit=3"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as res:
            if res.status == 200:
                data = json.loads(res.read().decode('utf-8'))
                items = data.get('results', [])
                for item in items:
                    preview = item.get('previewUrl')
                    if preview:
                        art = item.get('artworkUrl100', '')
                        if art:
                            art = art.replace('100x100bb', '300x300bb')
                        return preview, art, item.get('trackName')
    except Exception:
        pass
    return None, None, None

def find_preview_for_song(song):
    title = song.get("titulo", "")
    artist = song.get("artista", "")
    cleaned_t = clean_title(title)
    
    artist_lower = artist.lower().strip()
    is_cover_artist = any(cover in artist_lower for cover in JUST_DANCE_COVER_ARTISTS)

    queries = []
    if not is_cover_artist:
        queries.append(f"{artist} {cleaned_t}")
        if cleaned_t != title:
            queries.append(f"{artist} {title}")
    
    queries.append(cleaned_t)
    if is_cover_artist:
        queries.append(f"{artist} {cleaned_t}")

    # 1. Intentar Deezer
    for q in queries:
        preview, cover, track_name = search_deezer(q)
        if preview:
            return {
                "preview_url": preview,
                "cover_art": cover,
                "source": "deezer",
                "matched_track": track_name
            }
        time.sleep(0.04)

    # 2. Si Deezer no encontró, intentar iTunes
    for q in queries:
        preview, cover, track_name = search_itunes(q)
        if preview:
            return {
                "preview_url": preview,
                "cover_art": cover,
                "source": "itunes",
                "matched_track": track_name
            }
        time.sleep(0.06)

    return {
        "preview_url": None,
        "cover_art": None,
        "source": None,
        "matched_track": None
    }

def main():
    print("Iniciando enriquecimiento musical (Deezer + Apple Music)...")
    
    if not os.path.exists(INPUT_JSON):
        print(f"Error: No se encontró {INPUT_JSON}")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        songs = json.load(f)

    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
            print(f"Caché cargada: {len(cache)} canciones existentes.")
        except Exception as e:
            print("Error cargando caché previa:", e)
            cache = {}

    total = len(songs)
    pending_songs = [s for s in songs if s.get("id") not in cache or not cache[s.get("id")].get("preview_url")]
    print(f"Total canciones: {total} | Pendientes por consultar: {len(pending_songs)}")

    cache_lock = threading.Lock()
    found_count = 0

    # Rellenar existentes
    for s in songs:
        cid = s.get("id")
        if cid in cache and cache[cid].get("preview_url"):
            s["preview_url"] = cache[cid]["preview_url"]
            s["cover_art"] = cache[cid].get("cover_art")
            found_count += 1

    if pending_songs:
        max_workers = 4
        completed = 0

        def process_song(song):
            res = find_preview_for_song(song)
            with cache_lock:
                cache[song.get("id")] = res
            return song, res

        print(f"Consultando APIs con {max_workers} hilos...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_song = {executor.submit(process_song, s): s for s in pending_songs}
            
            for future in as_completed(future_to_song):
                s, res = future.result()
                completed += 1
                if res.get("preview_url"):
                    s["preview_url"] = res["preview_url"]
                    s["cover_art"] = res.get("cover_art")
                    found_count += 1

                if completed % 50 == 0 or completed == len(pending_songs):
                    print(f"Progreso: {completed}/{len(pending_songs)} procesadas | Total con preview: {found_count}/{total}...")
                    with cache_lock:
                        with open(CACHE_FILE, "w", encoding="utf-8") as cf:
                            json.dump(cache, cf, ensure_ascii=False, indent=2)

    # Guardar caché final
    with open(CACHE_FILE, "w", encoding="utf-8") as cf:
        json.dump(cache, cf, ensure_ascii=False, indent=2)

    # Guardar canciones_just_dance.json
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)
    print(f"Actualizado: {OUTPUT_JSON}")

    # Guardar data.js
    with open(OUTPUT_JS, "w", encoding="utf-8") as f:
        f.write("const JUST_DANCE_SONGS = ")
        json.dump(songs, f, ensure_ascii=False, indent=2)
        f.write(";\n")
    print(f"Actualizado: {OUTPUT_JS}")

    print(f"\n========================================================")
    print(f"ENRIQUECIMIENTO FINALIZADO:")
    print(f"Canciones con extracto de audio: {found_count} de {total} ({found_count/total*100:.1f}%)")
    print(f"========================================================")

if __name__ == "__main__":
    main()
