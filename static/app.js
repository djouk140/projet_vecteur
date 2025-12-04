// Configuration
const API_BASE_URL = window.location.origin;

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const minYear = document.getElementById('minYear');
const maxYear = document.getElementById('maxYear');
const genresFilter = document.getElementById('genresFilter');
const resultsCount = document.getElementById('resultsCount');
const resultsSection = document.getElementById('resultsSection');
const filmsGrid = document.getElementById('filmsGrid');
const recommendationSection = document.getElementById('recommendationSection');
const recommendationsGrid = document.getElementById('recommendationsGrid');
const recommendationSubtitle = document.getElementById('recommendationSubtitle');
const statsSection = document.getElementById('statsSection');
const statsGrid = document.getElementById('statsGrid');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');
const filmModal = document.getElementById('filmModal');
const closeModal = document.getElementById('closeModal');
const filmDetails = document.getElementById('filmDetails');

// Load stats on page load
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    
    // Add event listeners
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
    closeModal.addEventListener('click', () => {
        filmModal.style.display = 'none';
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === filmModal) {
            filmModal.style.display = 'none';
        }
    });
});

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        if (!response.ok) throw new Error('Failed to load stats');
        
        const stats = await response.json();
        displayStats(stats);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Display statistics
function displayStats(stats) {
    statsSection.style.display = 'block';
    statsGrid.innerHTML = `
        <div class="stat-item">
            <span class="stat-value">${stats.total_films || 0}</span>
            <span class="stat-label">Films</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">${stats.total_embeddings || 0}</span>
            <span class="stat-label">Embeddings</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">${stats.min_year || 'N/A'}</span>
            <span class="stat-label">Année min</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">${stats.max_year || 'N/A'}</span>
            <span class="stat-label">Année max</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">${stats.unique_genres || 0}</span>
            <span class="stat-label">Genres</span>
        </div>
    `;
}

// Handle search
async function handleSearch() {
    const query = searchInput.value.trim();
    if (!query) {
        showError('Veuillez entrer une requête de recherche');
        return;
    }

    hideError();
    showLoading();
    resultsSection.style.display = 'none';
    recommendationSection.style.display = 'none';

    try {
        const k = parseInt(document.getElementById('resultsCount').value) || 10;
        const params = new URLSearchParams({
            q: query,
            k: k
        });

        if (minYear.value) params.append('min_year', minYear.value);
        if (maxYear.value) params.append('max_year', maxYear.value);
        if (genresFilter.value) params.append('genres', genresFilter.value);

        const response = await fetch(`${API_BASE_URL}/search?${params}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erreur lors de la recherche');
        }

        const data = await response.json();
        displayResults(data);
    } catch (error) {
        showError(`Erreur: ${error.message}`);
        console.error('Search error:', error);
    } finally {
        hideLoading();
    }
}

// Display search results
async function displayResults(data) {
    if (!data.recommendations || data.recommendations.length === 0) {
        showError('Aucun résultat trouvé');
        return;
    }

    resultsSection.style.display = 'block';
    resultsCount.textContent = `${data.count} résultat(s) trouvé(s)`;
    
    // Create cards first with placeholders
    filmsGrid.innerHTML = data.recommendations.map(film => 
        createFilmCard(film.film, film.distance)
    ).join('');

    // Add click listeners to film cards
    document.querySelectorAll('.film-card').forEach(card => {
        card.addEventListener('click', () => {
            const filmId = card.dataset.filmId;
            loadFilmDetails(filmId);
            loadRecommendations(filmId);
        });
    });

    // Load poster images asynchronously
    await loadPosterImages(data.recommendations, '.films-grid');
}


// Get poster image URL
async function getFilmPoster(title, year = null) {
    try {
        // Try to get poster from our API endpoint
        try {
            const response = await fetch(`${API_BASE_URL}/api/poster/${encodeURIComponent(title)}${year ? `?year=${year}` : ''}`);
            if (response.ok) {
                const data = await response.json();
                if (data.poster_url) {
                    return data.poster_url;
                }
            }
        } catch (e) {
            // Continue to fallback
        }
        
        // Fallback to placeholder
        return getPlaceholderImage(title);
    } catch (error) {
        console.error('Error fetching poster:', error);
        return getPlaceholderImage(title);
    }
}

// Get placeholder image with title
function getPlaceholderImage(title) {
    // Utiliser un service de placeholder qui affiche le titre
    const encodedTitle = encodeURIComponent(title);
    return `https://via.placeholder.com/300x450/6366f1/ffffff?text=${encodedTitle}`;
}

// Create film card HTML with poster
function createFilmCard(film, distance = null, posterUrl = null) {
    const genres = film.genres ? film.genres.map(g => 
        `<span class="genre-tag">${escapeHtml(g)}</span>`
    ).join('') : '';
    
    const synopsis = film.synopsis ? 
        `<p class="film-synopsis">${escapeHtml(film.synopsis.substring(0, 120))}${film.synopsis.length > 120 ? '...' : ''}</p>` : '';

    // Use provided poster or placeholder
    const imageUrl = posterUrl || getPlaceholderImage(film.title);
    const similarityPercent = distance !== null ? ((1 - distance) * 100).toFixed(0) : null;

    return `
        <div class="film-card" data-film-id="${film.id}">
            <div class="film-poster-container">
                <img src="${imageUrl}" alt="${escapeHtml(film.title)}" class="film-poster" loading="lazy" 
                     onerror="this.src='${getPlaceholderImage(film.title)}'; this.onerror=null;">
                <div class="film-overlay">
                    ${film.year ? `<div class="film-year-badge">${film.year}</div>` : ''}
                    ${similarityPercent ? `<div class="similarity-badge">${similarityPercent}%</div>` : ''}
                </div>
            </div>
            <div class="film-card-content">
                <h3 class="film-title">${escapeHtml(film.title)}</h3>
                ${genres ? `<div class="film-genres">${genres}</div>` : ''}
                ${synopsis ? `<p class="film-synopsis">${synopsis}</p>` : ''}
                ${distance !== null ? `<div class="film-distance">Similarité: <span class="distance-value">${(1 - distance).toFixed(3)}</span></div>` : ''}
            </div>
        </div>
    `;
}

// Load film details
async function loadFilmDetails(filmId) {
    try {
        const response = await fetch(`${API_BASE_URL}/films/${filmId}`);
        if (!response.ok) throw new Error('Failed to load film details');
        
        const film = await response.json();
        displayFilmDetails(film);
        filmModal.style.display = 'flex';
    } catch (error) {
        showError(`Erreur lors du chargement des détails: ${error.message}`);
        console.error('Film details error:', error);
    }
}

// Display film details in modal
function displayFilmDetails(film) {
    const genres = film.genres ? film.genres.join(', ') : 'Non spécifié';
    const cast = film.cast ? film.cast.join(', ') : 'Non spécifié';
    const synopsis = film.synopsis || 'Aucune description disponible';

    filmDetails.innerHTML = `
        <div class="film-details">
            <h2 class="film-details-title">${escapeHtml(film.title)}</h2>
            ${film.year ? `<div class="film-details-year">Année: ${film.year}</div>` : ''}
            
            <div class="film-details-section">
                <h3>Genres</h3>
                <p>${escapeHtml(genres)}</p>
            </div>
            
            ${cast !== 'Non spécifié' ? `
            <div class="film-details-section">
                <h3>Cast</h3>
                <p>${escapeHtml(cast)}</p>
            </div>
            ` : ''}
            
            <div class="film-details-section">
                <h3>Synopsis</h3>
                <p>${escapeHtml(synopsis)}</p>
            </div>
        </div>
    `;
}

// Load recommendations for a film
async function loadRecommendations(filmId) {
    try {
        const k = parseInt(document.getElementById('resultsCount').value) || 10;
        const response = await fetch(`${API_BASE_URL}/recommend/by-film/${filmId}?k=${k}`);
        
        if (!response.ok) throw new Error('Failed to load recommendations');
        
        const data = await response.json();
        
        if (data.recommendations && data.recommendations.length > 0) {
            recommendationSection.style.display = 'block';
            recommendationSubtitle.textContent = `Films similaires au film ID "${data.query_film_id}"`;
            
            // Create cards first with placeholders
            recommendationsGrid.innerHTML = data.recommendations.map(rec => 
                createFilmCard(rec.film, rec.distance)
            ).join('');

            // Add click listeners
            document.querySelectorAll('#recommendationsGrid .film-card').forEach(card => {
                card.addEventListener('click', () => {
                    const id = card.dataset.filmId;
                    loadFilmDetails(id);
                    loadRecommendations(id);
                });
            });

            // Load poster images asynchronously
            await loadPosterImages(data.recommendations, '#recommendationsGrid');
        }
    } catch (error) {
        console.error('Recommendations error:', error);
    }
}

// Load poster images for films (supports different containers)
async function loadPosterImages(recommendations, containerSelector = '.films-grid') {
    const container = document.querySelector(containerSelector);
    if (!container) return;

    const promises = recommendations.map(async (rec) => {
        const film = rec.film;
        const cardElement = container.querySelector(`.film-card[data-film-id="${film.id}"]`);
        if (!cardElement) return;

        try {
            // Try to get poster from API or use placeholder
            const posterUrl = await getFilmPoster(film.title, film.year);
            const img = cardElement.querySelector('.film-poster');
            if (img && img.src !== posterUrl) {
                img.src = posterUrl;
            }
        } catch (error) {
            console.error(`Error loading poster for ${film.title}:`, error);
        }
    });

    await Promise.all(promises);
}

// Utility functions
function showLoading() {
    loading.style.display = 'block';
    searchBtn.disabled = true;
    searchBtn.querySelector('.btn-text').style.display = 'none';
    searchBtn.querySelector('.btn-loader').style.display = 'inline';
}

function hideLoading() {
    loading.style.display = 'none';
    searchBtn.disabled = false;
    searchBtn.querySelector('.btn-text').style.display = 'inline';
    searchBtn.querySelector('.btn-loader').style.display = 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

function hideError() {
    errorMessage.style.display = 'none';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

