// Configuration
const API_BASE_URL = window.location.origin;

// DOM Elements
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loginFormElement = document.getElementById('loginFormElement');
const registerFormElement = document.getElementById('registerFormElement');
const showRegisterLink = document.getElementById('showRegister');
const showLoginLink = document.getElementById('showLogin');
const errorMessage = document.getElementById('errorMessage');

// Switch between login and register forms
showRegisterLink.addEventListener('click', (e) => {
    e.preventDefault();
    loginForm.style.display = 'none';
    registerForm.style.display = 'block';
    hideError();
});

showLoginLink.addEventListener('click', (e) => {
    e.preventDefault();
    registerForm.style.display = 'none';
    loginForm.style.display = 'block';
    hideError();
});

// Login form submission
loginFormElement.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();

    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
        showError('Veuillez remplir tous les champs');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Erreur de connexion');
        }

        // Rediriger vers la page principale
        window.location.href = '/';
    } catch (error) {
        showError(error.message || 'Erreur lors de la connexion');
    }
});

// Register form submission
registerFormElement.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();

    const username = document.getElementById('registerUsername').value.trim();
    const email = document.getElementById('registerEmail').value.trim();
    const password = document.getElementById('registerPassword').value;
    const gender = document.getElementById('registerGender').value || null;

    if (!username || !email || !password) {
        showError('Veuillez remplir tous les champs obligatoires');
        return;
    }

    if (username.length < 3) {
        showError('Le nom d\'utilisateur doit contenir au moins 3 caractères');
        return;
    }

    if (password.length < 6) {
        showError('Le mot de passe doit contenir au moins 6 caractères');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ username, email, password, gender })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Erreur lors de l\'inscription');
        }

        // Rediriger vers la page principale
        window.location.href = '/';
    } catch (error) {
        showError(error.message || 'Erreur lors de l\'inscription');
    }
});

// Utility functions
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

// Check if user is already logged in
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            credentials: 'include'
        });

        if (response.ok) {
            // User is already logged in, redirect to main page
            window.location.href = '/';
        }
    } catch (error) {
        // Not logged in, stay on login page
    }
});

