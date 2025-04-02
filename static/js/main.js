// Wait for DOM content to be loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    feather.replace();
    
    // Show current year in the footer
    const yearSpan = document.querySelector('.current-year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Check API health status on page load
    checkApiHealth();
    
    // Add event listener for API health check button if it exists
    const healthCheckBtn = document.querySelector('[href="/api/health"]');
    if (healthCheckBtn) {
        healthCheckBtn.addEventListener('click', function(e) {
            e.preventDefault();
            checkApiHealth(true);
        });
    }
});

/**
 * Check API health and update UI accordingly
 * @param {boolean} showAlert - Whether to show alert with health status
 */
function checkApiHealth(showAlert = false) {
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            const statusIndicator = document.querySelector('.api-status');
            if (statusIndicator) {
                statusIndicator.classList.remove('bg-danger', 'bg-success', 'bg-warning');
                
                if (data.status === 'healthy') {
                    statusIndicator.classList.add('bg-success');
                    statusIndicator.setAttribute('title', 'API is healthy');
                } else {
                    statusIndicator.classList.add('bg-danger');
                    statusIndicator.setAttribute('title', 'API is not healthy');
                }
            }
            
            if (showAlert) {
                if (data.status === 'healthy') {
                    showNotification('API Status: Healthy', 'success');
                } else {
                    showNotification('API Status: ' + data.status, 'danger');
                }
            }
        })
        .catch(error => {
            console.error('Health check failed:', error);
            const statusIndicator = document.querySelector('.api-status');
            if (statusIndicator) {
                statusIndicator.classList.remove('bg-success', 'bg-warning');
                statusIndicator.classList.add('bg-danger');
                statusIndicator.setAttribute('title', 'Could not connect to API');
            }
            
            if (showAlert) {
                showNotification('Could not connect to API', 'danger');
            }
        });
}

/**
 * Show a notification message
 * @param {string} message - The message to display
 * @param {string} type - The alert type (success, danger, warning, info)
 */
function showNotification(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.style.top = '1rem';
    alertDiv.style.right = '1rem';
    alertDiv.style.zIndex = '9999';
    
    // Add message
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to document
    document.body.appendChild(alertDiv);
    
    // Remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.classList.remove('show');
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.parentNode.removeChild(alertDiv);
                }
            }, 150);
        }
    }, 5000);
}
