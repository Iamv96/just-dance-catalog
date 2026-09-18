// Aplicación Interactiva de Catálogo Just Dance Legacy con Multiselección
document.addEventListener('DOMContentLoaded', () => {
  // State
  let allSongs = [];
  let filteredSongs = [];
  let currentView = 'grid'; // 'grid' | 'table'
  let pageSize = 60;
  let currentPage = 1;

  // Multiselect State Sets
  const selectedEditions = new Set();
  const selectedGenres = new Set();
  const selectedLanguages = new Set();
  const selectedDifficulties = new Set();
  const selectedCoaches = new Set();

  // DOM Elements
  const searchInput = document.getElementById('search-input');
  const clearSearchBtn = document.getElementById('clear-search-btn');
  const sortSelect = document.getElementById('sort-select');
  const toggleFiltersBtn = document.getElementById('toggle-filters-btn');
  const filtersPanel = document.getElementById('filters-panel');
  const activeFiltersCountBadge = document.getElementById('active-filters-count-badge');
  const activeFiltersBar = document.getElementById('active-filters-bar');
  const activeChips = document.getElementById('active-chips');
  const resetAllFiltersBtn = document.getElementById('reset-all-filters-btn');
  const resultsCount = document.getElementById('results-count');
  const songsGrid = document.getElementById('songs-grid');
  const songsTableContainer = document.getElementById('songs-table-container');
  const songsTableBody = document.getElementById('songs-table-body');
  const noResults = document.getElementById('no-results');
  const clearFiltersEmptyBtn = document.getElementById('clear-filters-empty-btn');
  const loadMoreBtn = document.getElementById('load-more-btn');
  const gridViewBtn = document.getElementById('grid-view-btn');
  const tableViewBtn = document.getElementById('table-view-btn');
  const exportBtn = document.getElementById('export-btn');
  const exportMenu = document.getElementById('export-menu');
  const exportCsvBtn = document.getElementById('export-csv-btn');
  const exportJsonBtn = document.getElementById('export-json-btn');

  // Stats Elements
  const statTotalSongs = document.getElementById('stat-total-songs');
  const statTotalEditions = document.getElementById('stat-total-editions');
  const statTotalGenres = document.getElementById('stat-total-genres');
  const statTotalLanguages = document.getElementById('stat-total-languages');

  // Audio Player State & Elements
  const audioPlayer = new Audio();
  let currentPlayingSong = null;
  let isAudioPlaying = false;
  let isAudioLoading = false;
  let previousVolume = 0.8;

  const audioPlayerBar = document.getElementById('audio-player-bar');
  const playerArt = document.getElementById('player-art');
  const playerDiscIcon = document.getElementById('player-disc-icon');
  const playerTitle = document.getElementById('player-title');
  const playerArtist = document.getElementById('player-artist');
  const playerEdition = document.getElementById('player-edition');
  const playerPlayBtn = document.getElementById('player-play-btn');
  const playerPlayIcon = document.getElementById('player-play-icon');
  const playerPauseIcon = document.getElementById('player-pause-icon');
  const playerPrevBtn = document.getElementById('player-prev-btn');
  const playerNextBtn = document.getElementById('player-next-btn');
  const playerCurrentTime = document.getElementById('player-current-time');
  const playerTotalTime = document.getElementById('player-total-time');
  const playerProgressBar = document.getElementById('player-progress-bar');
  const playerProgressFill = document.getElementById('player-progress-fill');
  const playerVolumeBtn = document.getElementById('player-volume-btn');
  const playerVolIconHigh = document.getElementById('player-vol-icon-high');
  const playerVolIconMuted = document.getElementById('player-vol-icon-muted');
  const playerVolumeSlider = document.getElementById('player-volume-slider');
  const playerCloseBtn = document.getElementById('player-close-btn');

  // 1. Carga de Datos
  function initData() {
    if (typeof JUST_DANCE_SONGS !== 'undefined' && Array.isArray(JUST_DANCE_SONGS)) {
      allSongs = JUST_DANCE_SONGS;
      setupApp();
    } else {
      fetch('canciones_just_dance.json')
        .then(res => res.json())
        .then(data => {
          allSongs = data;
          setupApp();
        })
        .catch(err => {
          console.error("Error al cargar canciones_just_dance.json:", err);
          resultsCount.textContent = "Error al cargar la base de datos de canciones";
        });
    }
  }

  // 2. Setup Inicial
  function setupApp() {
    updateHeaderStats();
    setupEditionMultiSelect();
    setupGenreMultiSelect();
    setupLanguageMultiSelect();
    setupDifficultyMultiSelect();
    setupCoachMultiSelect();
    applyFiltersAndSort();
    bindEvents();
  }

  function updateHeaderStats() {
    statTotalSongs.textContent = allSongs.length.toLocaleString();
    const uniqueEditions = new Set(allSongs.map(s => s.edicion));
    const uniqueGenres = new Set(allSongs.map(s => s.genero));
    const uniqueLanguages = new Set(allSongs.map(s => s.idioma));
    statTotalEditions.textContent = uniqueEditions.size;
    statTotalGenres.textContent = uniqueGenres.size;
    statTotalLanguages.textContent = uniqueLanguages.size;
  }

  // --- MULTISELECT CONTROLLERS ---

  function setupMultiSelect({
    containerId,
    triggerId,
    dropdownId,
    optionsId,
    searchId,
    selectAllId,
    clearAllId,
    items,
    counts,
    selectedSet,
    defaultLabel,
    itemTypeLabel
  }) {
    const container = document.getElementById(containerId);
    const trigger = document.getElementById(triggerId);
    const optionsContainer = document.getElementById(optionsId);
    const searchInput = searchId ? document.getElementById(searchId) : null;
    const selectAllBtn = document.getElementById(selectAllId);
    const clearAllBtn = document.getElementById(clearAllId);

    // Populate options
    function renderOptions(filterQuery = '') {
      optionsContainer.innerHTML = '';
      const q = filterQuery.toLowerCase().trim();

      items.forEach(item => {
        const itemStr = String(item);
        if (q && !itemStr.toLowerCase().includes(q)) {
          return;
        }

        const count = counts[itemStr] || 0;
        const label = document.createElement('label');
        label.className = 'multiselect-option';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = itemStr;
        checkbox.checked = selectedSet.has(itemStr);

        checkbox.addEventListener('change', () => {
          if (checkbox.checked) {
            selectedSet.add(itemStr);
          } else {
            selectedSet.delete(itemStr);
          }
          updateTriggerText();
          applyFiltersAndSort();
        });

        const customBox = document.createElement('span');
        customBox.className = 'custom-checkbox';

        const optLabel = document.createElement('span');
        optLabel.className = 'option-label';
        optLabel.textContent = itemStr;

        const optCount = document.createElement('span');
        optCount.className = 'option-count';
        optCount.textContent = count;

        label.appendChild(checkbox);
        label.appendChild(customBox);
        label.appendChild(optLabel);
        if (count > 0) label.appendChild(optCount);

        optionsContainer.appendChild(label);
      });
    }

    function updateTriggerText() {
      const textSpan = trigger.querySelector('.trigger-text');
      if (selectedSet.size === 0) {
        textSpan.innerHTML = defaultLabel;
      } else if (selectedSet.size === 1) {
        const first = Array.from(selectedSet)[0];
        textSpan.innerHTML = `${first} <span class="trigger-badge">1</span>`;
      } else {
        textSpan.innerHTML = `${selectedSet.size} ${itemTypeLabel} <span class="trigger-badge">${selectedSet.size}</span>`;
      }
    }

    // Toggle dropdown open/close
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = container.classList.contains('open');
      closeAllDropdowns();
      if (!isOpen) {
        container.classList.add('open');
        if (searchInput) {
          searchInput.focus();
        }
      }
    });

    // Search filter inside dropdown
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        renderOptions(searchInput.value);
      });
      searchInput.addEventListener('click', (e) => e.stopPropagation());
    }

    // Select All
    if (selectAllBtn) {
      selectAllBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        items.forEach(item => selectedSet.add(String(item)));
        renderOptions(searchInput ? searchInput.value : '');
        updateTriggerText();
        applyFiltersAndSort();
      });
    }

    // Clear All
    if (clearAllBtn) {
      clearAllBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        selectedSet.clear();
        renderOptions(searchInput ? searchInput.value : '');
        updateTriggerText();
        applyFiltersAndSort();
      });
    }

    renderOptions();
    updateTriggerText();

    return {
      renderOptions,
      updateTriggerText
    };
  }

  let editionController, genreController, langController, diffController, coachController;

  function setupEditionMultiSelect() {
    const counts = {};
    allSongs.forEach(s => counts[s.edicion] = (counts[s.edicion] || 0) + 1);
    const sortedEditions = Object.keys(counts).sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));

    editionController = setupMultiSelect({
      containerId: 'edition-multiselect',
      triggerId: 'edition-trigger',
      dropdownId: 'edition-dropdown',
      optionsId: 'edition-options',
      searchId: 'edition-search',
      selectAllId: 'edition-select-all',
      clearAllId: 'edition-clear-all',
      items: sortedEditions,
      counts,
      selectedSet: selectedEditions,
      defaultLabel: 'Todas las Ediciones',
      itemTypeLabel: 'ediciones'
    });
  }

  function setupGenreMultiSelect() {
    const counts = {};
    allSongs.forEach(s => counts[s.genero] = (counts[s.genero] || 0) + 1);
    const sortedGenres = Object.keys(counts).sort((a, b) => counts[b] - counts[a]);

    genreController = setupMultiSelect({
      containerId: 'genre-multiselect',
      triggerId: 'genre-trigger',
      dropdownId: 'genre-dropdown',
      optionsId: 'genre-options',
      searchId: 'genre-search',
      selectAllId: 'genre-select-all',
      clearAllId: 'genre-clear-all',
      items: sortedGenres,
      counts,
      selectedSet: selectedGenres,
      defaultLabel: 'Todos los Géneros',
      itemTypeLabel: 'géneros'
    });
  }

  function setupLanguageMultiSelect() {
    const counts = {};
    allSongs.forEach(s => counts[s.idioma] = (counts[s.idioma] || 0) + 1);
    const priority = ["Spanglish", "Español", "Inglés", "Coreano", "Japonés", "Portugués", "Francés", "Chino", "Italiano", "Alemán", "Holandés", "Instrumental"];
    const sortedLangs = Object.keys(counts).sort((a, b) => {
      const idxA = priority.indexOf(a);
      const idxB = priority.indexOf(b);
      if (idxA !== -1 && idxB !== -1) return idxA - idxB;
      if (idxA !== -1) return -1;
      if (idxB !== -1) return 1;
      return counts[b] - counts[a];
    });

    langController = setupMultiSelect({
      containerId: 'language-multiselect',
      triggerId: 'language-trigger',
      dropdownId: 'language-dropdown',
      optionsId: 'language-options',
      searchId: null,
      selectAllId: 'language-select-all',
      clearAllId: 'language-clear-all',
      items: sortedLangs,
      counts,
      selectedSet: selectedLanguages,
      defaultLabel: 'Todos los Idiomas',
      itemTypeLabel: 'idiomas'
    });
  }

  function setupDifficultyMultiSelect() {
    const container = document.getElementById('difficulty-multiselect');
    const trigger = document.getElementById('difficulty-trigger');
    const selectAllBtn = document.getElementById('difficulty-select-all');
    const clearAllBtn = document.getElementById('difficulty-clear-all');
    const checkboxes = document.querySelectorAll('#difficulty-options input[type="checkbox"]');

    function updateTriggerText() {
      const textSpan = trigger.querySelector('.trigger-text');
      if (selectedDifficulties.size === 0) {
        textSpan.innerHTML = 'Cualquier dificultad';
      } else if (selectedDifficulties.size === 1) {
        const d = Array.from(selectedDifficulties)[0];
        textSpan.innerHTML = `${d}★ <span class="trigger-badge">1</span>`;
      } else {
        textSpan.innerHTML = `${selectedDifficulties.size} dif. <span class="trigger-badge">${selectedDifficulties.size}</span>`;
      }
    }

    checkboxes.forEach(cb => {
      cb.addEventListener('change', () => {
        if (cb.checked) {
          selectedDifficulties.add(cb.value);
        } else {
          selectedDifficulties.delete(cb.value);
        }
        updateTriggerText();
        applyFiltersAndSort();
      });
    });

    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = container.classList.contains('open');
      closeAllDropdowns();
      if (!isOpen) container.classList.add('open');
    });

    selectAllBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      ['1', '2', '3', '4'].forEach(d => selectedDifficulties.add(d));
      checkboxes.forEach(cb => cb.checked = true);
      updateTriggerText();
      applyFiltersAndSort();
    });

    clearAllBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      selectedDifficulties.clear();
      checkboxes.forEach(cb => cb.checked = false);
      updateTriggerText();
      applyFiltersAndSort();
    });

    diffController = {
      updateTriggerText,
      renderOptions: () => {
        checkboxes.forEach(cb => cb.checked = selectedDifficulties.has(cb.value));
      }
    };
  }

  function getCoachDisplayLabel(numStr) {
    switch (numStr) {
      case '1': return 'Solo (1)';
      case '2': return 'Dúo (2)';
      case '3': return 'Trío (3)';
      case '4': return 'Cuarteto (4)';
      default: return `${numStr} bailarines`;
    }
  }

  function setupCoachMultiSelect() {
    const counts = {};
    allSongs.forEach(s => {
      const c = String(s.coaches || 1);
      counts[c] = (counts[c] || 0) + 1;
    });

    const uniqueCoaches = Object.keys(counts).sort((a, b) => Number(a) - Number(b));

    const coachLabels = {
      '1': '👤 Solo (1)',
      '2': '👥 Dúo (2)',
      '3': '👥👤 Trío (3)',
      '4': '👥👥 Cuarteto (4)',
      '6': '👥 6 Bailarines (6)'
    };

    function getCoachOptionLabel(numStr) {
      return coachLabels[numStr] || `👥 ${numStr} Bailarines (${numStr})`;
    }

    const container = document.getElementById('coach-multiselect');
    const trigger = document.getElementById('coach-trigger');
    const optionsContainer = document.getElementById('coach-options');
    const selectAllBtn = document.getElementById('coach-select-all');
    const clearAllBtn = document.getElementById('coach-clear-all');

    function renderOptions() {
      optionsContainer.innerHTML = '';
      uniqueCoaches.forEach(cStr => {
        const count = counts[cStr] || 0;
        const label = document.createElement('label');
        label.className = 'multiselect-option';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = cStr;
        checkbox.checked = selectedCoaches.has(cStr);

        checkbox.addEventListener('change', () => {
          if (checkbox.checked) {
            selectedCoaches.add(cStr);
          } else {
            selectedCoaches.delete(cStr);
          }
          updateTriggerText();
          applyFiltersAndSort();
        });

        const customBox = document.createElement('span');
        customBox.className = 'custom-checkbox';

        const optLabel = document.createElement('span');
        optLabel.className = 'option-label';
        optLabel.textContent = getCoachOptionLabel(cStr);

        const optCount = document.createElement('span');
        optCount.className = 'option-count';
        optCount.textContent = count;

        label.appendChild(checkbox);
        label.appendChild(customBox);
        label.appendChild(optLabel);
        if (count > 0) label.appendChild(optCount);

        optionsContainer.appendChild(label);
      });
    }

    function updateTriggerText() {
      const textSpan = trigger.querySelector('.trigger-text');
      if (selectedCoaches.size === 0) {
        textSpan.innerHTML = 'Cualquier cantidad';
      } else if (selectedCoaches.size === 1) {
        const c = Array.from(selectedCoaches)[0];
        textSpan.innerHTML = `${getCoachDisplayLabel(c)} <span class="trigger-badge">1</span>`;
      } else {
        textSpan.innerHTML = `${selectedCoaches.size} tipos <span class="trigger-badge">${selectedCoaches.size}</span>`;
      }
    }

    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = container.classList.contains('open');
      closeAllDropdowns();
      if (!isOpen) container.classList.add('open');
    });

    selectAllBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      uniqueCoaches.forEach(c => selectedCoaches.add(c));
      renderOptions();
      updateTriggerText();
      applyFiltersAndSort();
    });

    clearAllBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      selectedCoaches.clear();
      renderOptions();
      updateTriggerText();
      applyFiltersAndSort();
    });

    renderOptions();
    updateTriggerText();

    coachController = {
      renderOptions,
      updateTriggerText
    };
  }

  function closeAllDropdowns() {
    document.querySelectorAll('.multiselect-container').forEach(c => c.classList.remove('open'));
  }

  function updateFilterBadge() {
    const totalFilters = selectedEditions.size + selectedGenres.size + selectedLanguages.size + selectedDifficulties.size + selectedCoaches.size;
    if (totalFilters > 0) {
      activeFiltersCountBadge.textContent = totalFilters;
      activeFiltersCountBadge.style.display = 'inline-flex';
      toggleFiltersBtn.classList.add('has-filters');
    } else {
      activeFiltersCountBadge.style.display = 'none';
      toggleFiltersBtn.classList.remove('has-filters');
    }
  }

  // 3. Normalización y Búsqueda
  function normalizeStr(str) {
    if (!str) return '';
    return str
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]/g, ' ')
      .trim();
  }

  function applyFiltersAndSort() {
    const query = normalizeStr(searchInput.value);
    const sortVal = sortSelect.value;

    clearSearchBtn.style.display = searchInput.value ? 'flex' : 'none';

    // Filtrado Multiselección
    filteredSongs = allSongs.filter(s => {
      // 1. Búsqueda por Nombre de Canción o Artista
      if (query) {
        const titleNorm = normalizeStr(s.titulo);
        const artistNorm = normalizeStr(s.artista);
        const mapNorm = normalizeStr(s.map_name);
        if (!titleNorm.includes(query) && !artistNorm.includes(query) && !mapNorm.includes(query)) {
          return false;
        }
      }

      // 2. Filtro Multiselección por Edición (OR dentro de ediciones)
      if (selectedEditions.size > 0 && !selectedEditions.has(s.edicion)) {
        return false;
      }

      // 3. Filtro Multiselección por Género (OR dentro de géneros)
      if (selectedGenres.size > 0 && !selectedGenres.has(s.genero)) {
        return false;
      }

      // 4. Filtro Multiselección por Idioma (OR dentro de idiomas)
      if (selectedLanguages.size > 0 && !selectedLanguages.has(s.idioma)) {
        return false;
      }

      // 5. Filtro Multiselección por Dificultad
      if (selectedDifficulties.size > 0 && !selectedDifficulties.has(String(s.dificultad))) {
        return false;
      }

      // 6. Filtro Multiselección por Bailarines (Coaches)
      if (selectedCoaches.size > 0 && !selectedCoaches.has(String(s.coaches || 1))) {
        return false;
      }

      return true;
    });

    // Ordenación
    filteredSongs.sort((a, b) => {
      switch (sortVal) {
        case 'title-asc':
          return a.titulo.localeCompare(b.titulo);
        case 'title-desc':
          return b.titulo.localeCompare(a.titulo);
        case 'artist-asc':
          return a.artista.localeCompare(b.artista);
        case 'diff-desc':
          return (b.dificultad || 0) - (a.dificultad || 0);
        case 'diff-asc':
          return (a.dificultad || 0) - (b.dificultad || 0);
        case 'coaches-desc':
          return (b.coaches || 1) - (a.coaches || 1);
        case 'coaches-asc':
          return (a.coaches || 1) - (b.coaches || 1);
        case 'edition-asc':
        default:
          const edDiff = a.edicion.localeCompare(b.edicion, undefined, { numeric: true });
          if (edDiff !== 0) return edDiff;
          return a.titulo.localeCompare(b.titulo);
      }
    });

    currentPage = 1;
    updateActiveChips();
    updateFilterBadge();
    renderResults();
  }

  // 4. Renderizado
  function renderResults() {
    const total = filteredSongs.length;
    resultsCount.textContent = `Mostrando ${total.toLocaleString()} ${total === 1 ? 'canción' : 'canciones'}`;

    if (total === 0) {
      songsGrid.style.display = 'none';
      songsTableContainer.style.display = 'none';
      loadMoreBtn.style.display = 'none';
      noResults.style.display = 'block';
      return;
    }

    noResults.style.display = 'none';
    const songsToDisplay = filteredSongs.slice(0, currentPage * pageSize);

    if (currentView === 'grid') {
      songsGrid.style.display = 'grid';
      songsTableContainer.style.display = 'none';
      renderGrid(songsToDisplay);
    } else {
      songsGrid.style.display = 'none';
      songsTableContainer.style.display = 'block';
      renderTable(songsToDisplay);
    }

    if (songsToDisplay.length < total) {
      loadMoreBtn.style.display = 'inline-block';
      loadMoreBtn.textContent = `Cargar más canciones (${songsToDisplay.length} de ${total})...`;
    } else {
      loadMoreBtn.style.display = 'none';
    }
  }

  function getGenreClass(genre) {
    const g = (genre || '').toLowerCase();
    if (g.includes('k-pop')) return 'genre-kpop';
    if (g.includes('j-pop')) return 'genre-jpop';
    if (g.includes('c-pop')) return 'genre-cpop';
    if (g.includes('latino') || g.includes('urbano') || g.includes('reggaeton')) return 'genre-latino';
    if (g.includes('rock')) return 'genre-rock';
    if (g.includes('dance') || g.includes('electro')) return 'genre-dance';
    if (g.includes('disco') || g.includes('funk')) return 'genre-disco';
    if (g.includes('r&b') || g.includes('soul')) return 'genre-rnb';
    if (g.includes('hip-hop') || g.includes('rap')) return 'genre-hiphop';
    if (g.includes('infantil')) return 'genre-kids';
    if (g.includes('disney') || g.includes('banda sonora')) return 'genre-disney';
    return 'genre-pop';
  }

  function getLanguageClass(lang) {
    switch (lang) {
      case 'Spanglish': return 'lang-spanglish';
      case 'Español': return 'lang-spanish';
      case 'Inglés': return 'lang-english';
      case 'Coreano': return 'lang-korean';
      case 'Japonés': return 'lang-japanese';
      case 'Chino': return 'lang-chinese';
      case 'Francés': return 'lang-french';
      case 'Portugués': return 'lang-portuguese';
      case 'Italiano': return 'lang-italian';
      case 'Alemán': return 'lang-german';
      case 'Holandés': return 'lang-dutch';
      case 'Instrumental': return 'lang-instrumental';
      default: return 'lang-english';
    }
  }

  function renderDifficultyStars(diff) {
    const d = Math.max(1, Math.min(4, diff || 1));
    let starsHtml = '';
    for (let i = 1; i <= 4; i++) {
      if (i <= d) {
        starsHtml += '★';
      } else {
        starsHtml += '<span class="diff-empty">★</span>';
      }
    }
    return `<div class="difficulty-stars" title="Dificultad: ${d}/4">${starsHtml}</div>`;
  }

  function getCoachEmoji(count) {
    switch (count) {
      case 1: return '👤 Solo';
      case 2: return '👥 Dúo';
      case 3: return '👥👤 Trío';
      case 4: return '👥👥 Cuarteto';
      default: return `👤 ${count} coaches`;
    }
  }

  function renderGrid(songs) {
    songsGrid.innerHTML = songs.map(s => {
      const isCurrent = currentPlayingSong && String(currentPlayingSong.id) === String(s.id);
      const isPlaying = isCurrent && isAudioPlaying;
      const isLoading = isCurrent && isAudioLoading;
      return `
      <article class="song-card ${isPlaying ? 'is-playing' : ''}" data-id="${escapeHtml(s.id)}">
        ${s.es_alternativa ? '<span class="alt-tag">Versión Alt</span>' : ''}
        <div class="song-card-body">
          <div class="song-thumb-wrap">
            ${s.cover_art 
              ? `<img src="${escapeHtml(s.cover_art)}" alt="Portada de ${escapeHtml(s.titulo)}" class="song-thumb-img" loading="lazy">` 
              : `<div class="song-thumb-fallback">🎵</div>`}
            <button 
              type="button" 
              class="song-play-btn ${isPlaying ? 'is-playing' : ''} ${isLoading ? 'is-loading' : ''}" 
              data-id="${escapeHtml(s.id)}" 
              title="${isPlaying ? 'Pausar extracto' : 'Reproducir extracto (30s)'}"
              aria-label="Reproducir extracto de ${escapeHtml(s.titulo)}"
            >
              <svg class="icon-play" viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
                <polygon points="6,4 20,12 6,20"/>
              </svg>
              <svg class="icon-pause" viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
                <rect x="6" y="4" width="4" height="16" rx="1"/>
                <rect x="14" y="4" width="4" height="16" rx="1"/>
              </svg>
              <div class="play-spinner"></div>
            </button>
          </div>
          <div class="song-card-info">
            <div class="song-card-header">
              <span class="edition-badge" title="Edición original: ${escapeHtml(s.edicion)}">${escapeHtml(s.edicion)}</span>
              <span class="coach-indicator" title="Cantidad de coaches">${getCoachEmoji(s.coaches)}</span>
            </div>
            <h3 class="song-title">${escapeHtml(s.titulo)}</h3>
            <p class="song-artist">${escapeHtml(s.artista)}</p>
          </div>
        </div>
        <div class="song-meta">
          <div class="meta-tags-row">
            <span class="genre-tag ${getGenreClass(s.genero)}">${escapeHtml(s.genero)}</span>
            <span class="lang-badge ${getLanguageClass(s.idioma)}">${escapeHtml(s.idioma)}</span>
          </div>
          ${renderDifficultyStars(s.dificultad)}
        </div>
      </article>
    `;
    }).join('');
  }

  function renderTable(songs) {
    songsTableBody.innerHTML = songs.map(s => {
      const isCurrent = currentPlayingSong && String(currentPlayingSong.id) === String(s.id);
      const isPlaying = isCurrent && isAudioPlaying;
      const isLoading = isCurrent && isAudioLoading;
      return `
      <tr class="${isPlaying ? 'table-row-playing' : ''}">
        <td>
          <div class="table-title-wrap">
            <button 
              type="button" 
              class="table-play-btn ${isPlaying ? 'is-playing' : ''} ${isLoading ? 'is-loading' : ''}" 
              data-id="${escapeHtml(s.id)}" 
              title="${isPlaying ? 'Pausar' : 'Reproducir (30s)'}"
              aria-label="Reproducir ${escapeHtml(s.titulo)}"
            >
              <svg class="icon-play" viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                <polygon points="6,4 20,12 6,20"/>
              </svg>
              <svg class="icon-pause" viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                <rect x="6" y="4" width="4" height="16" rx="1"/>
                <rect x="14" y="4" width="4" height="16" rx="1"/>
              </svg>
              <div class="play-spinner"></div>
            </button>
            ${s.cover_art 
              ? `<img src="${escapeHtml(s.cover_art)}" alt="" class="table-thumb" loading="lazy">` 
              : `<div class="table-thumb-fallback">🎵</div>`}
            <div class="table-title">
              ${escapeHtml(s.titulo)}
              ${s.es_alternativa ? ' <span class="alt-tag" style="position:static; display:inline-block; font-size:9px;">ALT</span>' : ''}
            </div>
          </div>
        </td>
        <td class="table-artist">${escapeHtml(s.artista)}</td>
        <td><span class="edition-badge">${escapeHtml(s.edicion)}</span></td>
        <td><span class="genre-tag ${getGenreClass(s.genero)}">${escapeHtml(s.genero)}</span></td>
        <td><span class="lang-badge ${getLanguageClass(s.idioma)}">${escapeHtml(s.idioma)}</span></td>
        <td>${renderDifficultyStars(s.dificultad)}</td>
        <td>${getCoachEmoji(s.coaches)}</td>
      </tr>
    `;
    }).join('');
  }

  function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // --- AUDIO CONTROLLER ---

  function findSongById(id) {
    return allSongs.find(s => String(s.id) === String(id));
  }

  function formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  }

  async function fetchPreviewOnTheFly(song) {
    const cleanT = (song.titulo || '').replace(/\s*\((just dance|alternate|cover).*?\)/gi, '').trim();
    const query = `${song.artista} ${cleanT}`;
    try {
      const res = await fetch(`https://api.deezer.com/search?q=${encodeURIComponent(query)}&limit=1`);
      const data = await res.json();
      if (data.data && data.data.length > 0) {
        const item = data.data[0];
        if (item.preview) {
          song.preview_url = item.preview;
          song.cover_art = item.album?.cover_medium || item.album?.cover;
          return song.preview_url;
        }
      }
    } catch (e) {
      try {
        const iRes = await fetch(`https://itunes.apple.com/search?term=${encodeURIComponent(query)}&entity=song&limit=1`);
        const iData = await iRes.json();
        if (iData.results && iData.results.length > 0) {
          const item = iData.results[0];
          song.preview_url = item.previewUrl;
          song.cover_art = item.artworkUrl100?.replace('100x100bb', '300x300bb');
          return song.preview_url;
        }
      } catch (err) {
        console.warn("Error en búsqueda en vivo:", err);
      }
    }
    return null;
  }

  async function playSong(song) {
    if (!song) return;

    if (currentPlayingSong && String(currentPlayingSong.id) === String(song.id)) {
      if (isAudioPlaying) {
        audioPlayer.pause();
      } else {
        audioPlayer.play().catch(e => console.warn(e));
      }
      return;
    }

    currentPlayingSong = song;
    updateFloatingPlayerInfo(song);
    audioPlayerBar.style.display = 'block';

    setLoadingState(true, song.id);

    let previewUrl = song.preview_url;
    if (!previewUrl) {
      previewUrl = await fetchPreviewOnTheFly(song);
    }

    if (!previewUrl) {
      setLoadingState(false, song.id);
      alert(`No se encontró un extracto de audio disponible para "${song.titulo}".`);
      return;
    }

    audioPlayer.src = previewUrl;
    audioPlayer.load();
    audioPlayer.play().then(() => {
      setLoadingState(false, song.id);
    }).catch(err => {
      console.warn("Error al reproducir audio:", err);
      setLoadingState(false, song.id);
    });
  }

  function togglePlayPause() {
    if (!currentPlayingSong) {
      if (filteredSongs.length > 0) {
        playSong(filteredSongs[0]);
      }
      return;
    }
    if (isAudioPlaying) {
      audioPlayer.pause();
    } else {
      audioPlayer.play().catch(e => console.warn(e));
    }
  }

  function playNextSong() {
    if (!currentPlayingSong || filteredSongs.length === 0) return;
    const currentIndex = filteredSongs.findIndex(s => String(s.id) === String(currentPlayingSong.id));
    if (currentIndex >= 0 && currentIndex < filteredSongs.length - 1) {
      playSong(filteredSongs[currentIndex + 1]);
    } else if (filteredSongs.length > 0) {
      playSong(filteredSongs[0]);
    }
  }

  function playPrevSong() {
    if (!currentPlayingSong || filteredSongs.length === 0) return;
    const currentIndex = filteredSongs.findIndex(s => String(s.id) === String(currentPlayingSong.id));
    if (currentIndex > 0) {
      playSong(filteredSongs[currentIndex - 1]);
    } else {
      playSong(filteredSongs[filteredSongs.length - 1]);
    }
  }

  function updateFloatingPlayerInfo(song) {
    playerTitle.textContent = song.titulo;
    playerArtist.textContent = song.artista;
    playerEdition.textContent = song.edicion;

    if (song.cover_art) {
      playerArt.src = song.cover_art;
      playerArt.style.display = 'block';
      playerDiscIcon.style.display = 'none';
    } else {
      playerArt.style.display = 'none';
      playerDiscIcon.style.display = 'flex';
    }
  }

  function setLoadingState(loading, songId) {
    isAudioLoading = loading;
    updatePlayStateUI();
  }

  function updatePlayStateUI() {
    // 1. Mini-player play/pause button & disc animation
    if (isAudioPlaying) {
      playerPlayIcon.style.display = 'none';
      playerPauseIcon.style.display = 'block';
      audioPlayerBar.classList.add('is-playing');
    } else {
      playerPlayIcon.style.display = 'block';
      playerPauseIcon.style.display = 'none';
      audioPlayerBar.classList.remove('is-playing');
    }

    // 2. Song Cards in Grid
    document.querySelectorAll('.song-card').forEach(card => {
      const cardId = card.dataset.id;
      const btn = card.querySelector('.song-play-btn');
      if (!btn) return;

      const isCurrent = currentPlayingSong && String(currentPlayingSong.id) === String(cardId);
      if (isCurrent && isAudioPlaying) {
        card.classList.add('is-playing');
        btn.classList.add('is-playing');
        btn.classList.remove('is-loading');
        btn.title = "Pausar extracto";
      } else if (isCurrent && isAudioLoading) {
        card.classList.remove('is-playing');
        btn.classList.remove('is-playing');
        btn.classList.add('is-loading');
        btn.title = "Cargando audio...";
      } else {
        card.classList.remove('is-playing');
        btn.classList.remove('is-playing');
        btn.classList.remove('is-loading');
        btn.title = "Reproducir extracto (30s)";
      }
    });

    // 3. Table Rows UI
    document.querySelectorAll('.table-play-btn').forEach(btn => {
      const btnId = btn.dataset.id;
      const isCurrent = currentPlayingSong && String(currentPlayingSong.id) === String(btnId);
      if (isCurrent && isAudioPlaying) {
        btn.classList.add('is-playing');
        btn.classList.remove('is-loading');
        btn.title = "Pausar";
      } else if (isCurrent && isAudioLoading) {
        btn.classList.remove('is-playing');
        btn.classList.add('is-loading');
        btn.title = "Cargando...";
      } else {
        btn.classList.remove('is-playing');
        btn.classList.remove('is-loading');
        btn.title = "Reproducir (30s)";
      }
    });
  }

  function closeAudioPlayer() {
    audioPlayer.pause();
    audioPlayer.src = '';
    currentPlayingSong = null;
    isAudioPlaying = false;
    isAudioLoading = false;
    audioPlayerBar.style.display = 'none';
    playerProgressFill.style.width = '0%';
    playerCurrentTime.textContent = '0:00';
    updatePlayStateUI();
  }

  // 5. Active Chips
  function updateActiveChips() {
    activeChips.innerHTML = '';
    let hasFilters = false;

    if (searchInput.value.trim()) {
      hasFilters = true;
      addChip(`Búsqueda: "${searchInput.value.trim()}"`, () => {
        searchInput.value = '';
        applyFiltersAndSort();
      });
    }

    selectedEditions.forEach(ed => {
      hasFilters = true;
      addChip(`Edición: ${ed}`, () => {
        selectedEditions.delete(ed);
        editionController.renderOptions();
        editionController.updateTriggerText();
        applyFiltersAndSort();
      });
    });

    selectedGenres.forEach(gen => {
      hasFilters = true;
      addChip(`Género: ${gen}`, () => {
        selectedGenres.delete(gen);
        genreController.renderOptions();
        genreController.updateTriggerText();
        applyFiltersAndSort();
      });
    });

    selectedLanguages.forEach(lang => {
      hasFilters = true;
      addChip(`Idioma: ${lang}`, () => {
        selectedLanguages.delete(lang);
        langController.renderOptions();
        langController.updateTriggerText();
        applyFiltersAndSort();
      });
    });

    selectedDifficulties.forEach(diff => {
      hasFilters = true;
      addChip(`Dificultad: ${diff}★`, () => {
        selectedDifficulties.delete(diff);
        diffController.renderOptions();
        diffController.updateTriggerText();
        applyFiltersAndSort();
      });
    });

    selectedCoaches.forEach(coach => {
      hasFilters = true;
      const label = getCoachDisplayLabel(coach);
      addChip(`Bailarines: ${label}`, () => {
        selectedCoaches.delete(coach);
        if (coachController) {
          coachController.renderOptions();
          coachController.updateTriggerText();
        }
        applyFiltersAndSort();
      });
    });

    activeFiltersBar.style.display = hasFilters ? 'flex' : 'none';
  }

  function addChip(text, onRemove) {
    const chip = document.createElement('div');
    chip.className = 'chip';
    chip.innerHTML = `<span>${text}</span><span class="chip-remove" title="Quitar filtro">✕</span>`;
    chip.querySelector('.chip-remove').addEventListener('click', onRemove);
    activeChips.appendChild(chip);
  }

  function resetAllFilters() {
    searchInput.value = '';
    selectedEditions.clear();
    selectedGenres.clear();
    selectedLanguages.clear();
    selectedDifficulties.clear();
    selectedCoaches.clear();
    sortSelect.value = 'edition-asc';

    editionController.renderOptions();
    editionController.updateTriggerText();
    genreController.renderOptions();
    genreController.updateTriggerText();
    langController.renderOptions();
    langController.updateTriggerText();
    diffController.renderOptions();
    diffController.updateTriggerText();
    if (coachController) {
      coachController.renderOptions();
      coachController.updateTriggerText();
    }

    applyFiltersAndSort();
  }

  // 6. Exportación de Datos
  function exportCSV() {
    const songsToExport = filteredSongs.length > 0 ? filteredSongs : allSongs;
    const headers = ["Título", "Artista", "Edición", "Género", "Idioma", "Dificultad", "Coaches", "Archivo", "ID"];
    const rows = songsToExport.map(s => [
      `"${(s.titulo || '').replace(/"/g, '""')}"`,
      `"${(s.artista || '').replace(/"/g, '""')}"`,
      `"${(s.edicion || '').replace(/"/g, '""')}"`,
      `"${(s.genero || '').replace(/"/g, '""')}"`,
      `"${(s.idioma || 'Inglés').replace(/"/g, '""')}"`,
      s.dificultad || 1,
      s.coaches || 1,
      `"${(s.archivo || '').replace(/"/g, '""')}"`,
      `"${(s.id || '').replace(/"/g, '""')}"`
    ]);

    const csvContent = "\uFEFF" + [headers.join(','), ...rows.map(r => r.join(','))].join('\r\n');
    downloadFile(csvContent, 'canciones_just_dance_filtradas.csv', 'text/csv;charset=utf-8;');
  }

  function exportJSON() {
    const songsToExport = filteredSongs.length > 0 ? filteredSongs : allSongs;
    const jsonContent = JSON.stringify(songsToExport, null, 2);
    downloadFile(jsonContent, 'canciones_just_dance_filtradas.json', 'application/json');
  }

  function downloadFile(content, fileName, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // 7. Event Listeners
  function bindEvents() {
    let debounceTimer;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        applyFiltersAndSort();
      }, 150);
    });

    clearSearchBtn.addEventListener('click', () => {
      searchInput.value = '';
      applyFiltersAndSort();
      searchInput.focus();
    });

    sortSelect.addEventListener('change', applyFiltersAndSort);
    resetAllFiltersBtn.addEventListener('click', resetAllFilters);
    clearFiltersEmptyBtn.addEventListener('click', resetAllFilters);

    loadMoreBtn.addEventListener('click', () => {
      currentPage++;
      renderResults();
    });

    // Toggle filters button
    if (toggleFiltersBtn && filtersPanel) {
      toggleFiltersBtn.addEventListener('click', () => {
        const isCollapsed = filtersPanel.classList.contains('collapsed');
        if (isCollapsed) {
          filtersPanel.classList.remove('collapsed');
          filtersPanel.classList.add('open');
          toggleFiltersBtn.setAttribute('aria-expanded', 'true');
          toggleFiltersBtn.classList.add('active');
        } else {
          filtersPanel.classList.add('collapsed');
          filtersPanel.classList.remove('open');
          toggleFiltersBtn.setAttribute('aria-expanded', 'false');
          toggleFiltersBtn.classList.remove('active');
          closeAllDropdowns();
        }
      });
    }

    // View toggle
    gridViewBtn.addEventListener('click', () => {
      currentView = 'grid';
      gridViewBtn.classList.add('active');
      tableViewBtn.classList.remove('active');
      renderResults();
    });

    tableViewBtn.addEventListener('click', () => {
      currentView = 'table';
      tableViewBtn.classList.add('active');
      gridViewBtn.classList.remove('active');
      renderResults();
    });

    // Export dropdown
    exportBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeAllDropdowns();
      exportMenu.classList.toggle('show');
    });

    // Close dropdowns on outside click
    document.addEventListener('click', (e) => {
      exportMenu.classList.remove('show');
      if (!e.target.closest('.multiselect-container')) {
        closeAllDropdowns();
      }
    });

    exportCsvBtn.addEventListener('click', () => {
      exportCSV();
      exportMenu.classList.remove('show');
    });

    exportJsonBtn.addEventListener('click', () => {
      exportJSON();
      exportMenu.classList.remove('show');
    });

    // Audio Playback Delegations
    songsGrid.addEventListener('click', (e) => {
      const btn = e.target.closest('.song-play-btn');
      if (btn) {
        e.stopPropagation();
        const id = btn.dataset.id;
        const song = findSongById(id);
        if (song) playSong(song);
      }
    });

    songsTableBody.addEventListener('click', (e) => {
      const btn = e.target.closest('.table-play-btn');
      if (btn) {
        e.stopPropagation();
        const id = btn.dataset.id;
        const song = findSongById(id);
        if (song) playSong(song);
      }
    });

    // Native Audio Events
    audioPlayer.addEventListener('play', () => {
      isAudioPlaying = true;
      isAudioLoading = false;
      updatePlayStateUI();
    });

    audioPlayer.addEventListener('pause', () => {
      isAudioPlaying = false;
      updatePlayStateUI();
    });

    audioPlayer.addEventListener('ended', () => {
      isAudioPlaying = false;
      updatePlayStateUI();
      playNextSong();
    });

    audioPlayer.addEventListener('timeupdate', () => {
      if (!audioPlayer.duration) return;
      const current = audioPlayer.currentTime;
      const total = audioPlayer.duration;
      playerCurrentTime.textContent = formatTime(current);
      playerTotalTime.textContent = formatTime(total);
      const percent = Math.min(100, (current / total) * 100);
      playerProgressFill.style.width = `${percent}%`;
    });

    audioPlayer.addEventListener('loadedmetadata', () => {
      playerTotalTime.textContent = formatTime(audioPlayer.duration);
    });

    audioPlayer.addEventListener('error', (e) => {
      console.warn("Audio error:", e);
      isAudioLoading = false;
      isAudioPlaying = false;
      updatePlayStateUI();
    });

    // Mini Player Controls
    playerPlayBtn.addEventListener('click', togglePlayPause);
    playerPrevBtn.addEventListener('click', playPrevSong);
    playerNextBtn.addEventListener('click', playNextSong);
    playerCloseBtn.addEventListener('click', closeAudioPlayer);

    // Progress Bar Seeking
    playerProgressBar.addEventListener('click', (e) => {
      if (!audioPlayer.duration) return;
      const rect = playerProgressBar.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const pct = Math.max(0, Math.min(1, clickX / rect.width));
      audioPlayer.currentTime = pct * audioPlayer.duration;
    });

    // Volume & Mute Controls
    playerVolumeSlider.addEventListener('input', () => {
      const val = parseFloat(playerVolumeSlider.value);
      audioPlayer.volume = val;
      if (val > 0) {
        audioPlayer.muted = false;
        previousVolume = val;
        playerVolIconHigh.style.display = 'block';
        playerVolIconMuted.style.display = 'none';
      } else {
        playerVolIconHigh.style.display = 'none';
        playerVolIconMuted.style.display = 'block';
      }
    });

    playerVolumeBtn.addEventListener('click', () => {
      if (audioPlayer.muted || audioPlayer.volume === 0) {
        audioPlayer.muted = false;
        audioPlayer.volume = previousVolume || 0.8;
        playerVolumeSlider.value = audioPlayer.volume;
        playerVolIconHigh.style.display = 'block';
        playerVolIconMuted.style.display = 'none';
      } else {
        previousVolume = audioPlayer.volume;
        audioPlayer.muted = true;
        playerVolumeSlider.value = 0;
        playerVolIconHigh.style.display = 'none';
        playerVolIconMuted.style.display = 'block';
      }
    });

    // Keyboard shortcut '/' to search, Escape to close/clear, Space to Play/Pause
    document.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== searchInput && !document.activeElement.closest('.multiselect-dropdown')) {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
      if (e.code === 'Space' && document.activeElement.tagName !== 'INPUT' && currentPlayingSong) {
        e.preventDefault();
        togglePlayPause();
      }
      if (e.key === 'Escape') {
        closeAllDropdowns();
        exportMenu.classList.remove('show');
        if (document.activeElement === searchInput) {
          searchInput.value = '';
          applyFiltersAndSort();
        }
      }
    });
  }

  // Arrancar
  initData();
});

