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

    // Initialize service category selection
    const serviceCategories = document.querySelectorAll('[onclick^="fetchServices"]');
    if (serviceCategories.length > 0) {
        // Click the first category to show services by default
        // serviceCategories[0].click();

        // Add active class on click
        serviceCategories.forEach(category => {
            category.addEventListener('click', function() {
                serviceCategories.forEach(c => {
                    c.querySelector('.card').classList.remove('border-primary');
                });
                this.querySelector('.card').classList.add('border-primary');
            });
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
 * Fetch services by service type
 * @param {string} serviceType - The service type to filter by
 */
function fetchServices(serviceType) {
    const servicesList = document.getElementById('services-list');
    if (!servicesList) return;
    
    // Show loading state
    servicesList.innerHTML = `
        <div class="col-12 text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">Loading services...</p>
        </div>
    `;
    
    // Update section title based on service type
    const sectionTitle = document.querySelector('#services-container h2');
    if (sectionTitle) {
        let title = 'Available Services';
        
        switch (serviceType) {
            case 'CAR_POOL':
                title = 'Car & Bike Pool Services';
                break;
            case 'GYM_FITNESS':
                title = 'Gym & Fitness Services';
                break;
            case 'HOUSEHOLD':
                title = 'Household Services';
                break;
            case 'MECHANICAL':
                title = 'Mechanical Services';
                break;
        }
        
        sectionTitle.textContent = title;
    }
    
    // Fetch services from API
    const apiUrl = `/api/services-ui?service_type=${serviceType}&status=AVAILABLE`;
    
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && Array.isArray(data)) {
                if (data.length === 0) {
                    // No services found
                    servicesList.innerHTML = `
                        <div class="col-12 text-center py-5">
                            <p>No ${serviceType.toLowerCase().replace('_', ' ')} services available at this time.</p>
                            <a href="/register" class="btn btn-outline-primary mt-3">Become a Service Provider</a>
                        </div>
                    `;
                } else {
                    // Render services
                    servicesList.innerHTML = '';
                    
                    data.forEach(service => {
                        let serviceIconClass = 'truck';
                        let serviceColorClass = 'primary';
                        
                        switch (service.service_type) {
                            case 'CAR_POOL':
                                serviceIconClass = 'truck';
                                serviceColorClass = 'primary';
                                break;
                            case 'GYM_FITNESS':
                                serviceIconClass = 'activity';
                                serviceColorClass = 'success';
                                break;
                            case 'HOUSEHOLD':
                                serviceIconClass = 'home';
                                serviceColorClass = 'info';
                                break;
                            case 'MECHANICAL':
                                serviceIconClass = 'tool';
                                serviceColorClass = 'warning';
                                break;
                        }
                        
                        const serviceCard = document.createElement('div');
                        serviceCard.className = 'col-md-4 mb-4';
                        serviceCard.innerHTML = `
                            <div class="card h-100">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between align-items-start mb-3">
                                        <div class="d-flex align-items-center">
                                            <i data-feather="${serviceIconClass}" class="me-2 text-${serviceColorClass}"></i>
                                            <h5 class="card-title mb-0">${service.name}</h5>
                                        </div>
                                        <span class="badge bg-${serviceColorClass}">${service.price ? '₹' + service.price : 'Contact'}</span>
                                    </div>
                                    <p class="card-text">${service.description}</p>
                                    <a href="/service/${service.id}" class="btn btn-sm btn-outline-${serviceColorClass} mt-2">View Details</a>
                                </div>
                                <div class="card-footer bg-transparent">
                                    <small class="text-muted">
                                        <i data-feather="user" class="me-1" style="width: 14px; height: 14px;"></i>
                                        ${service.provider_name || 'Service Provider'}
                                    </small>
                                </div>
                            </div>
                        `;
                        
                        servicesList.appendChild(serviceCard);
                    });
                    
                    // Re-initialize feather icons for new content
                    feather.replace();
                }
            } else {
                throw new Error('Invalid response format');
            }
        })
        .catch(error => {
            console.error('Error fetching services:', error);
            
            // Show error message
            servicesList.innerHTML = `
                <div class="col-12 text-center py-5">
                    <div class="alert alert-danger">
                        <i data-feather="alert-triangle" class="me-2"></i>
                        Error loading services. Please try again later.
                    </div>
                </div>
            `;
            
            feather.replace();
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
