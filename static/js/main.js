// Main JavaScript for Local Service Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }

    // Setup navbar behavior based on authentication
    setupNavbar();

    // Setup logout functionality
    setupLogout();
});

/**
 * Setup navbar based on authentication status
 */
function setupNavbar() {
    const token = localStorage.getItem('access_token');
    const username = localStorage.getItem('username');
    const role = localStorage.getItem('role');

    const navbarNav = document.getElementById('navbarNav');
    
    if (!navbarNav) return;
    
    if (token && username) {
        // User is logged in, update navbar
        const authLinks = navbarNav.querySelector('.navbar-nav:last-child');
        
        if (authLinks) {
            authLinks.innerHTML = `
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" 
                       data-bs-toggle="dropdown" aria-expanded="false">
                        <i data-feather="user" class="feather-icon-sm"></i>
                        ${username}
                    </a>
                    <ul class="dropdown-menu" aria-labelledby="userDropdown">
                        <li><a class="dropdown-item" href="/profile">My Profile</a></li>
                        <li><a class="dropdown-item" href="/wallet">My Wallet</a></li>
                        <li><a class="dropdown-item" href="/bookings">My Bookings</a></li>
                        ${role === 'power_user' ? '<li><a class="dropdown-item" href="/provider/services">My Services</a></li>' : ''}
                        ${role === 'admin' ? '<li><a class="dropdown-item" href="/admin/dashboard">Admin Dashboard</a></li>' : ''}
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="#" id="logout-link">Logout</a></li>
                    </ul>
                </li>
            `;
            
            // Re-initialize Feather icons after DOM update
            if (typeof feather !== 'undefined') {
                feather.replace();
            }
        }
    }
}

/**
 * Setup logout functionality
 */
function setupLogout() {
    const logoutLink = document.getElementById('logout-link');
    
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Clear localStorage
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_id');
            localStorage.removeItem('username');
            localStorage.removeItem('role');
            
            // Redirect to home page
            window.location.href = '/';
        });
    }
}

/**
 * Format a date string to a more readable format
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

/**
 * Format currency for display
 * @param {number} amount - Amount to format
 * @returns {string} Formatted amount
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Display rating stars
 * @param {number} rating - Rating value (1-5)
 * @returns {string} HTML for rating stars
 */
function displayRatingStars(rating) {
    let starsHtml = '';
    
    for (let i = 1; i <= 5; i++) {
        if (i <= rating) {
            starsHtml += '<i data-feather="star" class="feather-icon-sm filled"></i>';
        } else {
            starsHtml += '<i data-feather="star" class="feather-icon-sm"></i>';
        }
    }
    
    return starsHtml;
}

/**
 * Add authorization header to fetch requests
 * @param {Object} options - Fetch options
 * @returns {Object} Updated fetch options with auth header
 */
function addAuthHeader(options = {}) {
    const token = localStorage.getItem('access_token');
    
    if (!token) return options;
    
    const headers = options.headers || {};
    
    return {
        ...options,
        headers: {
            ...headers,
            'Authorization': `Bearer ${token}`
        }
    };
}

/**
 * Make authenticated API requests
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @returns {Promise} Fetch promise
 */
function apiRequest(url, options = {}) {
    return fetch(url, addAuthHeader(options))
        .then(response => {
            if (!response.ok) {
                // If response is 401 Unauthorized, redirect to login
                if (response.status === 401) {
                    localStorage.removeItem('access_token');
                    window.location.href = '/auth/login';
                    throw new Error('Session expired. Please login again.');
                }
                return response.json().then(data => {
                    throw new Error(data.message || 'API request failed');
                });
            }
            return response.json();
        });
}

/**
 * Show an alert message
 * @param {string} message - The message to display
 * @param {string} type - Alert type (success, danger, warning, info)
 * @param {string} containerId - ID of the container element
 */
function showAlert(message, type = 'info', containerId = 'alert-container') {
    const container = document.getElementById(containerId);
    
    if (!container) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    container.innerHTML = '';
    container.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}
