// Kickoff Kings - Frontend JavaScript

let playersData = [];
let draftedPlayers = [];
let predictionsLoaded = false;
let currentUser = null;
let authToken = localStorage.getItem('auth_token');
let currentDraftSessionId = null;

// DOM Elements
const loadDataBtn = document.getElementById('load-data-btn');
const getRecommendationsBtn = document.getElementById('get-recommendations-btn');
const addDraftedBtn = document.getElementById('add-drafted-btn');
const loading = document.getElementById('loading');
const draftTbody = document.getElementById('draft-tbody');
const draftedList = document.getElementById('drafted-list');
const draftedPlayerInput = document.getElementById('drafted-player-input');

// Event Listeners
loadDataBtn.addEventListener('click', loadPlayerPredictions);
getRecommendationsBtn.addEventListener('click', getDraftRecommendations);
addDraftedBtn.addEventListener('click', addDraftedPlayer);
draftedPlayerInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        addDraftedPlayer();
    }
});

// Load player predictions (auto-calculates for upcoming season)
async function loadPlayerPredictions() {
    setLoading(true);
    loadDataBtn.disabled = true;
    
    try {
        // First, get the base player data
        const scrapeResponse = await fetch('/api/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const scrapeData = await scrapeResponse.json();
        
        if (!scrapeData.success) {
            throw new Error(scrapeData.error || 'Failed to load player data');
        }
        
        // Then get predictions for the upcoming season (always 17 games)
        const predictResponse = await fetch('/api/predictions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const predictData = await predictResponse.json();
        
        if (!predictData.success) {
            throw new Error(predictData.error || 'Failed to generate predictions');
        }
        
        playersData = predictData.players;
        predictionsLoaded = true;
        getRecommendationsBtn.disabled = false;
        
        showNotification('Player predictions loaded successfully!', 'success');
        
        // Auto-load recommendations
        getDraftRecommendations();
        
    } catch (error) {
        console.error('Error loading predictions:', error);
        showNotification('Error: ' + error.message, 'error');
    } finally {
        setLoading(false);
        loadDataBtn.disabled = false;
    }
}

// Get draft recommendations
async function getDraftRecommendations() {
    if (!predictionsLoaded) {
        showNotification('Please load player predictions first', 'error');
        return;
    }
    
    setLoading(true);
    getRecommendationsBtn.disabled = true;
    
    try {
        const numTeams = parseInt(document.getElementById('num-teams').value) || 12;
        const draftPosition = parseInt(document.getElementById('draft-position').value) || 1;
        
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }
        
        const response = await fetch('/api/draft-assistant', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                num_teams: numTeams,
                draft_position: draftPosition,
                already_drafted: draftedPlayers,
                session_id: currentDraftSessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayDraftTable(data.recommendations);
            updateDraftInfo(data);
            
            // Save session ID if returned
            if (data.session_id) {
                currentDraftSessionId = data.session_id;
            }
            
            // Display AI analysis if available (premium feature)
            if (data.ai_analysis) {
                displayAIAnalysis(data.ai_analysis);
            }
            
            showNotification('Draft recommendations updated!', 'success');
        } else {
            if (data.error === 'Premium subscription required') {
                showNotification('Premium subscription required for AI analysis', 'error');
            } else {
                showNotification('Error: ' + data.error, 'error');
            }
        }
    } catch (error) {
        console.error('Error getting recommendations:', error);
        showNotification('Error: ' + error.message, 'error');
    } finally {
        setLoading(false);
        getRecommendationsBtn.disabled = false;
    }
}

// Display draft table
function displayDraftTable(recommendations) {
    draftTbody.innerHTML = '';
    
    if (recommendations.length === 0) {
        draftTbody.innerHTML = '<tr><td colspan="7" class="empty-state">No recommendations available</td></tr>';
        return;
    }
    
    recommendations.forEach((player, index) => {
        const row = document.createElement('tr');
        
        const rank = index + 1;
        const name = player.Name || 'N/A';
        const team = player.Team || 'N/A';
        const position = player.Position || 'N/A';
        const posRank = player['Position Rank'] || 'N/A';
        const predictedPoints = (player['Predicted Points'] || 0).toFixed(1);
        
        row.innerHTML = `
            <td><strong>${rank}</strong></td>
            <td><strong>${name}</strong></td>
            <td>${team}</td>
            <td><span class="position-badge position-${position}">${position}</span></td>
            <td>${posRank}</td>
            <td><strong>${predictedPoints}</strong></td>
            <td><button class="btn btn-small btn-secondary" onclick="draftPlayer('${name.replace(/'/g, "\\'")}')">Draft</button></td>
        `;
        
        draftTbody.appendChild(row);
    });
}

// Update draft info
function updateDraftInfo(data) {
    const draftInfo = document.getElementById('draft-info');
    if (draftInfo) {
        document.getElementById('current-pick').textContent = data.current_pick;
        document.getElementById('round-number').textContent = data.round_number;
        document.getElementById('pick-in-round').textContent = data.pick_in_round;
        draftInfo.style.display = 'block';
    }
}

// Display AI analysis (premium feature)
function displayAIAnalysis(analysis) {
    let analysisDiv = document.getElementById('ai-analysis');
    if (!analysisDiv) {
        analysisDiv = document.createElement('div');
        analysisDiv.id = 'ai-analysis';
        analysisDiv.className = 'card';
        analysisDiv.style.marginTop = '1rem';
        
        const title = document.createElement('h3');
        title.className = 'card-title';
        title.textContent = '🤖 AI Draft Analysis';
        analysisDiv.appendChild(title);
        
        const content = document.createElement('div');
        content.id = 'ai-analysis-content';
        content.style.padding = '1rem';
        content.style.backgroundColor = '#1a1a1a';
        content.style.borderRadius = '8px';
        content.style.whiteSpace = 'pre-wrap';
        content.style.lineHeight = '1.6';
        analysisDiv.appendChild(content);
        
        const draftSection = document.querySelector('#draft');
        if (draftSection) {
            draftSection.querySelector('.container').appendChild(analysisDiv);
        }
    }
    
    document.getElementById('ai-analysis-content').textContent = analysis;
}

// Add drafted player
function addDraftedPlayer() {
    const playerName = draftedPlayerInput.value.trim();
    
    if (!playerName) {
        return;
    }
    
    // Try to find exact match or close match
    const matchedPlayer = playersData.find(p => 
        p.Name.toLowerCase() === playerName.toLowerCase() ||
        p.Name.toLowerCase().includes(playerName.toLowerCase())
    );
    
    const nameToAdd = matchedPlayer ? matchedPlayer.Name : playerName;
    
    if (!draftedPlayers.includes(nameToAdd)) {
        draftedPlayers.push(nameToAdd);
        updateDraftedList();
        draftedPlayerInput.value = '';
        
        // Refresh recommendations if already loaded
        if (predictionsLoaded) {
            getDraftRecommendations();
        }
    } else {
        showNotification('Player already in drafted list', 'error');
    }
}

// Remove drafted player
function removeDraftedPlayer(playerName) {
    draftedPlayers = draftedPlayers.filter(p => p !== playerName);
    updateDraftedList();
    
    // Refresh recommendations if already loaded
    if (predictionsLoaded) {
        getDraftRecommendations();
    }
}

// Update drafted players list
function updateDraftedList() {
    if (draftedPlayers.length === 0) {
        draftedList.innerHTML = '<p class="empty-state">No players drafted yet</p>';
        return;
    }
    
    draftedList.innerHTML = draftedPlayers.map(player => `
        <span class="drafted-player-tag">
            ${player}
            <button class="remove-btn" onclick="removeDraftedPlayer('${player.replace(/'/g, "\\'")}')">×</button>
        </span>
    `).join('');
}

// Draft player from recommendations
function draftPlayer(playerName) {
    if (!draftedPlayers.includes(playerName)) {
        draftedPlayers.push(playerName);
        updateDraftedList();
        getDraftRecommendations();
        showNotification(`${playerName} added to drafted players`, 'success');
    }
}

// Set loading state
function setLoading(isLoading) {
    loading.style.display = isLoading ? 'flex' : 'none';
    if (isLoading) {
        loadDataBtn.disabled = true;
        getRecommendationsBtn.disabled = true;
    }
}

// Show notification
function showNotification(message, type) {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification status-message status-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        max-width: 400px;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Authentication functions
async function signup(email, password, fullName = '') {
    try {
        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email,
                password,
                full_name: fullName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            authToken = data.session.access_token;
            localStorage.setItem('auth_token', authToken);
            currentUser = data.user;
            updateAuthUI();
            showNotification('Account created successfully!', 'success');
            return true;
        } else {
            showNotification('Error: ' + data.error, 'error');
            return false;
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
        return false;
    }
}

async function login(email, password) {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email,
                password
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            authToken = data.session.access_token;
            localStorage.setItem('auth_token', authToken);
            currentUser = data.user;
            updateAuthUI();
            showNotification('Logged in successfully!', 'success');
            return true;
        } else {
            showNotification('Error: ' + data.error, 'error');
            return false;
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
        return false;
    }
}

async function logout() {
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        authToken = null;
        currentUser = null;
        currentDraftSessionId = null;
        localStorage.removeItem('auth_token');
        updateAuthUI();
        showNotification('Logged out successfully', 'success');
    } catch (error) {
        console.error('Logout error:', error);
    }
}

async function checkAuth() {
    if (!authToken) return;
    
    try {
        const response = await fetch('/api/auth/me', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        if (data.success) {
            currentUser = data.user;
            updateAuthUI();
        } else {
            authToken = null;
            localStorage.removeItem('auth_token');
        }
    } catch (error) {
        console.error('Auth check error:', error);
        authToken = null;
        localStorage.removeItem('auth_token');
    }
}

function updateAuthUI() {
    const authSection = document.getElementById('auth-section');
    const userSection = document.getElementById('user-section');
    
    if (currentUser) {
        if (authSection) authSection.style.display = 'none';
        if (userSection) {
            userSection.style.display = 'block';
            const userEmail = userSection.querySelector('#user-email');
            const userTier = userSection.querySelector('#user-tier');
            const upgradeBtn = document.getElementById('upgrade-btn');
            
            if (userEmail) userEmail.textContent = currentUser.email;
            if (userTier) {
                const tier = currentUser.subscription_tier || 'free';
                userTier.textContent = tier;
                userTier.className = tier === 'premium' ? 'premium-badge' : 'free-badge';
            }
            if (upgradeBtn) {
                upgradeBtn.style.display = (currentUser.subscription_tier === 'premium') ? 'none' : 'inline-block';
            }
        }
    } else {
        if (authSection) authSection.style.display = 'block';
        if (userSection) userSection.style.display = 'none';
    }
}

async function upgradeToPremium() {
    if (!currentUser) {
        showNotification('Please log in to upgrade', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/stripe/create-checkout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        if (data.success) {
            window.location.href = data.url;
        } else {
            showNotification('Error: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

// Initialize auth on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
});
