# 💃 Catálogo Interactivo de Canciones Just Dance 🕺

Aplicación web interactiva y scripts de procesamiento/enriquecimiento para explorar el catálogo completo de canciones de la saga **Just Dance**.

## ✨ Características

- 🔍 **Buscador interactivo**: Filtrado en tiempo real por título, artista y juego.
- 🎛️ **Filtros avanzados**: Filtra por año, género musical, dificultad y modo de juego.
- 🎵 **Previsualizaciones de audio**: Escucha fragmentos de las canciones directamente desde la interfaz.
- 📊 **Visualización moderna**: Diseño responsive y dinámico con temas visuales.
- 🐍 **Scripts de enriquecimiento de datos**:
  - `extractor.py`: Extracción y normalización de la base de datos de canciones.
  - `enrich_genres.py`: Enriquecimiento automático de géneros musicales.
  - `enrich_previews.py`: Búsqueda y vinculación de previews de audio.

## 🚀 Uso local

Simplemente abre `index.html` en tu navegador web favorito o sírvelo con cualquier servidor local:

```bash
# Con Python
python -m http.server 8000
```
Luego visita `http://localhost:8000` en tu navegador.
