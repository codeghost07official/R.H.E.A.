// ==========================================================================
// R.H.E.A. - FRONTEND LOGIC & PYWEBVIEW BRIDGE
// ==========================================================================

// Wait for the pywebview API to be ready before enabling interaction
window.addEventListener('pywebviewready', function() {
    addLog('[SYSTEM] PyWebView Bridge established. Frontend connected to Core Engine.', 'rhea');
    updateStatus('ONLINE - LISTENING');
});

/**
 * Appends a new line to the center console log.
 */
function addLog(message, sender) {
    const chatContainer = document.getElementById('chat-container');
    const logLine = document.createElement('div');
    
    logLine.className = `console-line ${sender}`;
    
    if (sender === 'user') {
        logLine.innerText = `[JAI] > ${message}`;
    } else {
        logLine.innerText = `${message}`;
    }

    chatContainer.appendChild(logLine);
    
    // Auto-scroll to the bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Grabs the text from the input box and sends it to the Python backend.
 */
function sendTextCommand() {
    const inputField = document.getElementById('user-input');
    const command = inputField.value.trim();

    if (command === "") return;

    addLog(command, 'user');
    inputField.value = '';
    
    if (window.pywebview && window.pywebview.api) {
        updateStatus('PROCESSING QUERY...');
        
        window.pywebview.api.process_text_command(command).then(function(response) {
            addLog(`[R.H.E.A.] ${response}`, 'rhea');
            updateStatus('ONLINE - LISTENING');
        }).catch(function(error) {
            addLog(`[ERROR] Communication failure: ${error}`, 'rhea');
            updateStatus('ERROR');
        });
    } else {
        addLog('[ERROR] PyWebView API not found.', 'rhea');
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendTextCommand();
    }
}

// ==========================================================================
// FUNCTIONS CALLED BY PYTHON BACKEND (TELEMETRY)
// ==========================================================================

function updateTelemetry(cpuPercent, ramString, ramPercent) {
    document.getElementById('cpu-val').innerText = `${cpuPercent}%`;
    document.getElementById('cpu-bar').style.width = `${cpuPercent}%`;

    document.getElementById('ram-val').innerText = ramString;
    document.getElementById('ram-bar').style.width = `${ramPercent}%`;
}

// NEW: Updates the Live Clock on the Dashboard
function updateDateTime(dateString, timeString) {
    const dateEl = document.getElementById('date-val');
    const timeEl = document.getElementById('time-val');
    
    if (dateEl) dateEl.innerText = dateString;
    if (timeEl) timeEl.innerText = timeString;
}

function updateStatus(statusText) {
    const statusEl = document.getElementById('system-status');
    if (statusEl) statusEl.innerText = statusText;
}

function updateLanguageUI(lang) {
    const langEl = document.getElementById('lang-status');
    if (langEl) langEl.innerText = lang;
}

function updateAutomationStatus(x, y, task) {
    const coordsEl = document.getElementById('mouse-coords');
    const taskEl = document.getElementById('last-task');
    
    if (coordsEl) coordsEl.innerText = `${x}, ${y}`;
    if (taskEl) taskEl.innerText = task;
}