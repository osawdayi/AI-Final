// Kickoff Kings - Frontend JavaScript

let playersData = [];
let draftedPlayers = [];
let predictionsLoaded = false;

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
        
        const response = await fetch('/api/draft-assistant', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                num_teams: numTeams,
                draft_position: draftPosition,
                already_drafted: draftedPlayers
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayDraftTable(data.recommendations);
            updateDraftInfo(data);
            showNotification('Draft recommendations updated!', 'success');
        } else {
            showNotification('Error: ' + data.error, 'error');
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
    document.getElementById('current-pick').textContent = data.current_pick;
    document.getElementById('round-number').textContent = data.round_number;
    document.getElementById('pick-in-round').textContent = data.pick_in_round;
    draftInfo.style.display = 'block';
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
