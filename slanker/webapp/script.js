// Slanker WebApp JavaScript
// Handles form submission, UI interactions, and Telegram WebApp integration

// Global variables
let socialMediaCount = 0;
const API_BASE_URL = window.location.hostname === 'localhost' ? 
    'http://localhost:8000' : 
    'https://slanker-api.onrender.com'; // API endpoint

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupFormHandlers();
    setupTelegramWebApp();
});

// Initialize the application
function initializeApp() {
    console.log('🚀 Slanker WebApp initialized');
    
    // Load theme preference
    loadThemePreference();
    
    // Add one social media input by default
    addSocialMedia();
    
    // Setup form validation
    setupFormValidation();
}

// Setup Telegram WebApp integration
function setupTelegramWebApp() {
    if (window.Telegram && window.Telegram.WebApp) {
        const tg = window.Telegram.WebApp;
        
        // Initialize Telegram WebApp
        tg.ready();
        
        // Apply Telegram theme
        applyTelegramTheme(tg);
        
        // Setup main button
        tg.MainButton.setText('🎯 Deploy Token');
        tg.MainButton.onClick(() => {
            document.getElementById('deployBtn').click();
        });
        
        // Enable closing confirmation
        tg.enableClosingConfirmation();
        
        console.log('📱 Telegram WebApp initialized');
    }
}

// Apply Telegram theme to app
function applyTelegramTheme(tg) {
    if (tg.colorScheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        updateThemeIcon('☀️');
    } else {
        document.documentElement.removeAttribute('data-theme');
        updateThemeIcon('🌙');
    }
}

// Theme management
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    
    if (currentTheme === 'dark') {
        document.documentElement.removeAttribute('data-theme');
        updateThemeIcon('🌙');
        localStorage.setItem('slanker-theme', 'light');
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        updateThemeIcon('☀️');
        localStorage.setItem('slanker-theme', 'dark');
    }
}

function updateThemeIcon(icon) {
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = icon;
    }
}

function loadThemePreference() {
    const savedTheme = localStorage.getItem('slanker-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        updateThemeIcon('☀️');
    }
}

// Form handlers
function setupFormHandlers() {
    const tokenForm = document.getElementById('tokenForm');
    if (tokenForm) {
        tokenForm.addEventListener('submit', handleFormSubmit);
    }
}

function setupFormValidation() {
    // Real-time validation for symbol field
    const symbolInput = document.getElementById('tokenSymbol');
    if (symbolInput) {
        symbolInput.addEventListener('input', function(e) {
            const value = e.target.value.toUpperCase().replace(/[^A-Z]/g, '');
            e.target.value = value;
        });
    }
    
    // Real-time validation for IPFS image
    const imageInput = document.getElementById('tokenImage');
    if (imageInput) {
        imageInput.addEventListener('blur', function(e) {
            const value = e.target.value;
            if (value && !value.startsWith('ipfs://')) {
                showToast('Image must be an IPFS URL starting with ipfs://', 'error');
                e.target.focus();
            }
        });
    }
    
    // Number input validation
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            const min = parseFloat(e.target.min);
            const max = parseFloat(e.target.max);
            const value = parseFloat(e.target.value);
            
            if (value < min) e.target.value = min;
            if (value > max) e.target.value = max;
        });
    });
}

// Social media management
function addSocialMedia() {
    socialMediaCount++;
    const container = document.getElementById('socialMediaContainer');
    
    const socialRow = document.createElement('div');
    socialRow.className = 'social-media-row';
    socialRow.id = `social-${socialMediaCount}`;
    
    socialRow.innerHTML = `
        <select class="form-select" name="socialPlatform" required>
            <option value="">Platform</option>
            <option value="x">𝕏 (Twitter)</option>
            <option value="telegram">Telegram</option>
            <option value="discord">Discord</option>
            <option value="github">GitHub</option>
            <option value="website">Website</option>
            <option value="medium">Medium</option>
        </select>
        <input 
            type="url" 
            class="form-input" 
            name="socialUrl" 
            placeholder="https://example.com/yourprofile"
            required
        />
        <button 
            type="button" 
            class="remove-social-btn" 
            onclick="removeSocialMedia('social-${socialMediaCount}')"
            title="Remove"
        >
            ❌
        </button>
    `;
    
    container.appendChild(socialRow);
}

function removeSocialMedia(rowId) {
    const row = document.getElementById(rowId);
    if (row) {
        row.remove();
    }
    
    // Ensure at least one social media row exists
    const container = document.getElementById('socialMediaContainer');
    if (container.children.length === 0) {
        addSocialMedia();
    }
}

// Form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const deployBtn = document.getElementById('deployBtn');
    const btnSpinner = document.getElementById('btnSpinner');
    const btnText = document.querySelector('.btn-text');
    
    try {
        // Show loading state
        deployBtn.disabled = true;
        deployBtn.classList.add('loading');
        btnText.textContent = '⏳ Deploying...';
        
        // Update Telegram main button
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.MainButton.setText('⏳ Deploying...');
            window.Telegram.WebApp.MainButton.showProgress();
        }
        
        // Collect form data
        const formData = collectFormData();
        
        // Validate form data
        if (!validateFormData(formData)) {
            return;
        }
        
        // Send deployment request
        const result = await deployToken(formData);
        
        if (result.success) {
            showSuccessResult(result);
            showToast('Token deployed successfully! 🎉', 'success');
        } else {
            showErrorResult(result.error || 'Deployment failed');
            showToast('Deployment failed. Please try again.', 'error');
        }
        
    } catch (error) {
        console.error('Deployment error:', error);
        showErrorResult('Network error or API unavailable');
        showToast('Network error. Please check your connection.', 'error');
    } finally {
        // Reset loading state
        deployBtn.disabled = false;
        deployBtn.classList.remove('loading');
        btnText.textContent = 'Generate & Deploy';
        
        // Reset Telegram main button
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.MainButton.setText('🎯 Deploy Token');
            window.Telegram.WebApp.MainButton.hideProgress();
        }
    }
}

// Collect form data
function collectFormData() {
    const formData = {
        name: document.getElementById('tokenName').value.trim(),
        symbol: document.getElementById('tokenSymbol').value.trim().toUpperCase(),
        image: document.getElementById('tokenImage').value.trim(),
        description: document.getElementById('tokenDescription').value.trim(),
        initialMarketCap: document.getElementById('initialMarketCap').value,
        vestingPercentage: parseInt(document.getElementById('vestingPercentage').value),
        vestingDurationDays: parseInt(document.getElementById('vestingDuration').value),
        creatorReward: parseInt(document.getElementById('creatorReward').value),
        socialMediaUrls: []
    };
    
    // Collect social media URLs
    const socialRows = document.querySelectorAll('.social-media-row');
    socialRows.forEach(row => {
        const platform = row.querySelector('select[name="socialPlatform"]').value;
        const url = row.querySelector('input[name="socialUrl"]').value.trim();
        
        if (platform && url) {
            formData.socialMediaUrls.push({
                platform: platform,
                url: url
            });
        }
    });
    
    return formData;
}

// Validate form data
function validateFormData(data) {
    // Required fields validation
    if (!data.name || !data.symbol || !data.image || !data.initialMarketCap) {
        showToast('Please fill in all required fields', 'error');
        return false;
    }
    
    // Symbol validation
    if (data.symbol.length < 3 || data.symbol.length > 5 || !/^[A-Z]+$/.test(data.symbol)) {
        showToast('Symbol must be 3-5 uppercase letters only', 'error');
        return false;
    }
    
    // IPFS image validation
    if (!data.image.startsWith('ipfs://')) {
        showToast('Image must be an IPFS URL starting with ipfs://', 'error');
        return false;
    }
    
    // Market cap validation
    const marketCap = parseFloat(data.initialMarketCap);
    if (isNaN(marketCap) || marketCap <= 0) {
        showToast('Initial market cap must be a positive number', 'error');
        return false;
    }
    
    return true;
}

// Deploy token via API
async function deployToken(formData) {
    const response = await fetch(`${API_BASE_URL}/deploy`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    });
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

// Show success result
function showSuccessResult(result) {
    const deploymentForm = document.getElementById('deploymentForm');
    const resultSection = document.getElementById('resultSection');
    const errorSection = document.getElementById('errorSection');
    
    // Hide form and error section
    deploymentForm.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Populate result data
    document.getElementById('tokenAddress').textContent = result.address;
    document.getElementById('basescanLink').href = result.basescanUrl;
    
    // Show result section
    resultSection.style.display = 'block';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Update Telegram main button
    if (window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.MainButton.setText('🚀 Deploy Another');
        window.Telegram.WebApp.MainButton.onClick(deployAnother);
    }
}

// Show error result
function showErrorResult(errorMessage) {
    const deploymentForm = document.getElementById('deploymentForm');
    const resultSection = document.getElementById('resultSection');
    const errorSection = document.getElementById('errorSection');
    
    // Hide form and result section
    deploymentForm.style.display = 'none';
    resultSection.style.display = 'none';
    
    // Populate error message
    document.getElementById('errorMessage').textContent = errorMessage;
    
    // Show error section
    errorSection.style.display = 'block';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Deploy another token
function deployAnother() {
    const deploymentForm = document.getElementById('deploymentForm');
    const resultSection = document.getElementById('resultSection');
    const errorSection = document.getElementById('errorSection');
    
    // Show form, hide results
    deploymentForm.style.display = 'block';
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Clear form but keep some values
    const tokenName = document.getElementById('tokenName');
    const tokenSymbol = document.getElementById('tokenSymbol');
    const tokenImage = document.getElementById('tokenImage');
    const tokenDescription = document.getElementById('tokenDescription');
    
    tokenName.value = '';
    tokenSymbol.value = '';
    tokenImage.value = '';
    tokenDescription.value = '';
    
    // Focus on first input
    tokenName.focus();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Reset Telegram main button
    if (window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.MainButton.setText('🎯 Deploy Token');
        window.Telegram.WebApp.MainButton.onClick(() => {
            document.getElementById('deployBtn').click();
        });
    }
}

// Try again after error
function tryAgain() {
    const deploymentForm = document.getElementById('deploymentForm');
    const errorSection = document.getElementById('errorSection');
    
    // Show form, hide error
    deploymentForm.style.display = 'block';
    errorSection.style.display = 'none';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Clear form data
function clearForm() {
    if (confirm('Are you sure you want to clear all form data?')) {
        // Clear all form inputs
        document.getElementById('tokenForm').reset();
        
        // Reset social media container
        const container = document.getElementById('socialMediaContainer');
        container.innerHTML = '';
        socialMediaCount = 0;
        addSocialMedia();
        
        // Reset default values
        document.getElementById('vestingPercentage').value = '10';
        document.getElementById('vestingDuration').value = '30';
        document.getElementById('creatorReward').value = '75';
        
        showToast('Form cleared successfully', 'success');
        
        // Clear form data from memory (security)
        setTimeout(() => {
            if (window.performance && window.performance.memory) {
                // Force garbage collection if available
                if (window.gc && typeof window.gc === 'function') {
                    window.gc();
                }
            }
        }, 100);
    }
}

// Copy to clipboard
async function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;
    
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard! 📋', 'success');
        
        // Visual feedback
        element.style.background = 'var(--success-color)';
        element.style.color = 'white';
        
        setTimeout(() => {
            element.style.background = '';
            element.style.color = '';
        }, 500);
        
    } catch (err) {
        console.error('Failed to copy:', err);
        
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        
        try {
            document.execCommand('copy');
            showToast('Copied to clipboard! 📋', 'success');
        } catch (fallbackErr) {
            showToast('Failed to copy. Please copy manually.', 'error');
        }
        
        document.body.removeChild(textArea);
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    
    // Remove existing classes
    toast.classList.remove('show', 'success', 'error');
    
    // Set message and type
    toast.textContent = message;
    if (type) {
        toast.classList.add(type);
    }
    
    // Show toast
    toast.classList.add('show');
    
    // Auto hide after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Memory cleanup function (called on form clear)
function clearSensitiveData() {
    // Clear any sensitive data from memory
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        if (input.type === 'password' || input.name.includes('key')) {
            input.value = '';
            // Overwrite input value in memory
            for (let i = 0; i < 10; i++) {
                input.value = Math.random().toString(36);
            }
            input.value = '';
        }
    });
}

// Handle browser back button and page unload
window.addEventListener('beforeunload', function(e) {
    // Clear sensitive data when leaving the page
    clearSensitiveData();
});

// Handle visibility change (tab switching)
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Clear sensitive data when tab becomes hidden
        clearSensitiveData();
    }
});

// Error handling for uncaught errors
window.addEventListener('error', function(e) {
    console.error('Uncaught error:', e.error);
    showToast('An unexpected error occurred. Please refresh and try again.', 'error');
});

// Handle network status changes
window.addEventListener('online', function() {
    showToast('Connection restored ✅', 'success');
});

window.addEventListener('offline', function() {
    showToast('Connection lost. Please check your network.', 'error');
});

// Export functions for global access
window.toggleTheme = toggleTheme;
window.addSocialMedia = addSocialMedia;
window.removeSocialMedia = removeSocialMedia;
window.clearForm = clearForm;
window.copyToClipboard = copyToClipboard;
window.deployAnother = deployAnother;
window.tryAgain = tryAgain;