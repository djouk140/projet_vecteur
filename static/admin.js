// Configuration
const API_BASE_URL = window.location.origin;

// DOM Elements
const kpiGrid = document.getElementById('kpiGrid');
const usersTableBody = document.getElementById('usersTableBody');
const sessionsTableBody = document.getElementById('sessionsTableBody');
const historyTableBody = document.getElementById('historyTableBody');
const watchedTableBody = document.getElementById('watchedTableBody');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');
const logoutBtn = document.getElementById('logoutBtn');
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Charts
let usersChart = null;
let searchesChart = null;

// Load dashboard on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    await checkAuth();
    
    // Load dashboard data
    await loadDashboard();
    
    // Setup tabs
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });
    
    // Logout
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
});

// Check authentication
async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            credentials: 'include'
        });
        
        if (!response.ok) {
            window.location.href = '/static/login.html';
            return;
        }
        
        const user = await response.json();
        if (user.role !== 'admin') {
            window.location.href = '/';
            return;
        }
    } catch (error) {
        window.location.href = '/static/login.html';
    }
}

// Load dashboard data
async function loadDashboard() {
    showLoading();
    try {
        const [dashboardData, usersData, sessionsData, historyData] = await Promise.all([
            fetch(`${API_BASE_URL}/api/admin/dashboard`, { credentials: 'include' }).then(r => r.json()),
            fetch(`${API_BASE_URL}/api/admin/users?limit=100`, { credentials: 'include' }).then(r => r.json()),
            fetch(`${API_BASE_URL}/api/admin/sessions?limit=100`, { credentials: 'include' }).then(r => r.json()),
            fetch(`${API_BASE_URL}/api/admin/search-history?limit=100`, { credentials: 'include' }).then(r => r.json())
        ]);
        
        displayKPI(dashboardData.kpi);
        displayCharts(dashboardData);
        displayUsers(usersData.users);
        displaySessions(sessionsData.sessions);
        displayHistory(historyData.history);
        
    } catch (error) {
        showError(`Erreur lors du chargement: ${error.message}`);
        console.error('Dashboard error:', error);
    } finally {
        hideLoading();
    }
}

// Display KPI
function displayKPI(kpi) {
    kpiGrid.innerHTML = `
        <div class="kpi-card">
            <div class="kpi-value">${kpi.total_users || 0}</div>
            <div class="kpi-label">Utilisateurs totaux</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">${kpi.total_admins || 0}</div>
            <div class="kpi-label">Administrateurs</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">${kpi.active_sessions || 0}</div>
            <div class="kpi-label">Sessions actives</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">${kpi.total_searches || 0}</div>
            <div class="kpi-label">Recherches totales</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">${kpi.total_watched || 0}</div>
            <div class="kpi-label">Films visionnés</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">${kpi.active_today || 0}</div>
            <div class="kpi-label">Actifs aujourd'hui</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">${kpi.searches_today || 0}</div>
            <div class="kpi-label">Recherches aujourd'hui</div>
        </div>
    `;
}

// Display charts
function displayCharts(data) {
    // Users chart
    const usersCtx = document.getElementById('usersChart');
    if (usersCtx && data.users_by_day) {
        if (usersChart) usersChart.destroy();
        usersChart = new Chart(usersCtx, {
            type: 'line',
            data: {
                labels: data.users_by_day.map(d => new Date(d.date).toLocaleDateString('fr-FR')),
                datasets: [{
                    label: 'Nouveaux utilisateurs',
                    data: data.users_by_day.map(d => d.count),
                    borderColor: 'rgb(99, 102, 241)',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#f1f5f9' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#cbd5e1' },
                        grid: { color: '#334155' }
                    },
                    x: {
                        ticks: { color: '#cbd5e1' },
                        grid: { color: '#334155' }
                    }
                }
            }
        });
    }
    
    // Searches chart
    const searchesCtx = document.getElementById('searchesChart');
    if (searchesCtx && data.searches_by_day) {
        if (searchesChart) searchesChart.destroy();
        searchesChart = new Chart(searchesCtx, {
            type: 'bar',
            data: {
                labels: data.searches_by_day.map(d => new Date(d.date).toLocaleDateString('fr-FR')),
                datasets: [{
                    label: 'Recherches',
                    data: data.searches_by_day.map(d => d.count),
                    backgroundColor: 'rgba(139, 92, 246, 0.6)',
                    borderColor: 'rgb(139, 92, 246)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#f1f5f9' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#cbd5e1' },
                        grid: { color: '#334155' }
                    },
                    x: {
                        ticks: { color: '#cbd5e1' },
                        grid: { color: '#334155' }
                    }
                }
            }
        });
    }
}

// Display users
function displayUsers(users) {
    if (!usersTableBody) return;
    
    usersTableBody.innerHTML = users.map(user => {
        const statusClass = user.is_blocked ? 'status-blocked' : 
                          user.is_active ? 'status-active' : 'status-inactive';
        const statusText = user.is_blocked ? 'Bloqué' : 
                          user.is_active ? 'Actif' : 'Inactif';
        const createdDate = new Date(user.created_at).toLocaleDateString('fr-FR');
        
        return `
            <tr>
                <td>${user.id}</td>
                <td>${escapeHtml(user.username)}</td>
                <td>${escapeHtml(user.email)}</td>
                <td><span class="status-badge">${user.role}</span></td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td>${createdDate}</td>
                <td>
                    <div class="action-buttons">
                        ${!user.is_blocked ? 
                            `<button class="action-btn danger" onclick="blockUser(${user.id})">Bloquer</button>` :
                            `<button class="action-btn" onclick="unblockUser(${user.id})">Débloquer</button>`
                        }
                        <button class="action-btn danger" onclick="deleteUser(${user.id})">Supprimer</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// Display sessions
function displaySessions(sessions) {
    if (!sessionsTableBody) return;
    
    sessionsTableBody.innerHTML = sessions.map(session => {
        const createdDate = new Date(session.created_at).toLocaleString('fr-FR');
        const expiresDate = new Date(session.expires_at).toLocaleString('fr-FR');
        const userAgent = session.user_agent ? session.user_agent.substring(0, 50) + '...' : 'N/A';
        
        return `
            <tr>
                <td>${session.id}</td>
                <td>${escapeHtml(session.username)}</td>
                <td>${session.ip_address || 'N/A'}</td>
                <td>${escapeHtml(userAgent)}</td>
                <td>${createdDate}</td>
                <td>${expiresDate}</td>
            </tr>
        `;
    }).join('');
}

// Display history
function displayHistory(history) {
    if (!historyTableBody) return;
    
    historyTableBody.innerHTML = history.map(item => {
        const date = new Date(item.created_at).toLocaleString('fr-FR');
        const filters = item.filters || {};
        let filtersText = '';
        if (filters.genres) filtersText += `Genres: ${filters.genres.join(', ')} `;
        if (filters.min_year) filtersText += `Année min: ${filters.min_year} `;
        if (filters.max_year) filtersText += `Année max: ${filters.max_year}`;
        
        return `
            <tr>
                <td>${item.id}</td>
                <td>${escapeHtml(item.username)}</td>
                <td>${escapeHtml(item.query_text)}</td>
                <td>${escapeHtml(filtersText || 'Aucun')}</td>
                <td>${item.results_count}</td>
                <td>${date}</td>
            </tr>
        `;
    }).join('');
}

// Switch tab
function switchTab(tabName) {
    tabButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}Tab`);
    });
}

// Block user
async function blockUser(userId) {
    if (!confirm('Êtes-vous sûr de vouloir bloquer cet utilisateur ?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/block`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            await loadDashboard();
        } else {
            throw new Error('Erreur lors du blocage');
        }
    } catch (error) {
        showError(`Erreur: ${error.message}`);
    }
}

// Unblock user
async function unblockUser(userId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/unblock`, {
            method: 'POST',
            credentials: 'include'
        });
        
        if (response.ok) {
            await loadDashboard();
        } else {
            throw new Error('Erreur lors du déblocage');
        }
    } catch (error) {
        showError(`Erreur: ${error.message}`);
    }
}

// Delete user
async function deleteUser(userId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ? Cette action est irréversible.')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (response.ok) {
            await loadDashboard();
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Erreur lors de la suppression');
        }
    } catch (error) {
        showError(`Erreur: ${error.message}`);
    }
}

// Handle logout
async function handleLogout() {
    try {
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        window.location.href = '/static/login.html';
    } catch (error) {
        window.location.href = '/static/login.html';
    }
}

// Utility functions
function showLoading() {
    if (loading) loading.style.display = 'block';
}

function hideLoading() {
    if (loading) loading.style.display = 'none';
}

function showError(message) {
    if (errorMessage) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Make functions available globally
window.blockUser = blockUser;
window.unblockUser = unblockUser;
window.deleteUser = deleteUser;
