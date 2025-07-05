// Admin Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    setupQuickActions();
});

function initializeCharts() {
    // Get data from template variables passed via data attributes
    const chartContainer = document.getElementById('chart-data');
    if (!chartContainer) return;
    
    const channelData = JSON.parse(chartContainer.dataset.channels || '{}');
    const categoryData = JSON.parse(chartContainer.dataset.categories || '[]');
    
    // Channel Performance Chart
    const channelCtx = document.getElementById('channelChart');
    if (channelCtx) {
        new Chart(channelCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Telegram', 'Discord', 'Twitter', 'Email'],
                datasets: [{
                    label: 'Posts Sent',
                    data: [
                        channelData.telegram || 0,
                        channelData.discord || 0,
                        channelData.twitter || 0,
                        channelData.email || 0
                    ],
                    backgroundColor: [
                        '#3B82F6',
                        '#7C3AED',
                        '#1DA1F2',
                        '#10B981'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Category Distribution Chart
    const categoryCtx = document.getElementById('categoryChart');
    if (categoryCtx && categoryData.length > 0) {
        const labels = categoryData.slice(0, 5).map(cat => cat.category);
        const data = categoryData.slice(0, 5).map(cat => cat.count);

        new Chart(categoryCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#EF4444',
                        '#F59E0B',
                        '#10B981',
                        '#3B82F6',
                        '#8B5CF6'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

function setupQuickActions() {
    // Force Scrape Button
    const scrapeBtn = document.querySelector('[data-action="force-scrape"]');
    if (scrapeBtn) {
        scrapeBtn.addEventListener('click', handleForceScrape);
    }

    // Test Notification Button
    const testBtn = document.querySelector('[data-action="test-notification"]');
    if (testBtn) {
        testBtn.addEventListener('click', handleTestNotification);
    }

    // Send Newsletter Button
    const newsletterBtn = document.querySelector('[data-action="send-newsletter"]');
    if (newsletterBtn) {
        newsletterBtn.addEventListener('click', handleSendNewsletter);
    }

    // Export Data Button
    const exportBtn = document.querySelector('[data-action="export-data"]');
    if (exportBtn) {
        exportBtn.addEventListener('click', handleExportData);
    }
}

function handleForceScrape() {
    if (confirm('Start manual scraping process?')) {
        showLoading('Starting scraper...');
        
        fetch('/api/admin/force-scrape', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                hideLoading();
                showNotification(data.message || 'Scraping started', 'success');
                setTimeout(() => location.reload(), 2000);
            })
            .catch(error => {
                hideLoading();
                showNotification('Error starting scrape: ' + error.message, 'error');
            });
    }
}

function handleTestNotification() {
    if (confirm('Send test notification to all channels?')) {
        showLoading('Sending test notification...');
        
        fetch('/api/admin/test-notification', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                hideLoading();
                showNotification(data.message || 'Test notification sent', 'success');
            })
            .catch(error => {
                hideLoading();
                showNotification('Error sending notification: ' + error.message, 'error');
            });
    }
}

function handleSendNewsletter() {
    if (confirm('Send newsletter to all subscribers?')) {
        showLoading('Sending newsletter...');
        
        fetch('/api/admin/send-newsletter', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                hideLoading();
                showNotification(data.message || 'Newsletter sent', 'success');
            })
            .catch(error => {
                hideLoading();
                showNotification('Error sending newsletter: ' + error.message, 'error');
            });
    }
}

function handleExportData() {
    showLoading('Preparing export...');
    window.location.href = '/api/admin/export-data';
    setTimeout(hideLoading, 2000);
}

function showLoading(message) {
    const loading = document.createElement('div');
    loading.id = 'loading-overlay';
    loading.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    loading.innerHTML = `
        <div class="bg-white rounded-lg p-6 flex items-center space-x-3">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span class="text-gray-700">${message}</span>
        </div>
    `;
    document.body.appendChild(loading);
}

function hideLoading() {
    const loading = document.getElementById('loading-overlay');
    if (loading) {
        loading.remove();
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}
