// ==========================================================================
// R.H.E.A. - FRONTEND LOGIC & ASYNCHRONOUS BRIDGE SIGNALLING
// ==========================================================================

window.addEventListener('pywebviewready', function() {
    addLog('[SYSTEM] PyWebView Bridge established. Frontend connected to Core Engine.', 'rhea');
    updateStatus('AWAITING WAKE WORD');
});

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
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function sendTextCommand() {
    const inputField = document.getElementById('user-input');
    const command = inputField.value.trim();

    if (command === "") return;

    addLog(command, 'user');
    inputField.value = '';
    
    if (window.pywebview && window.pywebview.api) {
        updateStatus('PROCESSING QUERY...');
        
        // Command is handed off to the backend asynchronously; Python returns "OK" immediately
        // and uses clear webview injection handles to print logs when rendering is complete.
        window.pywebview.api.process_text_command(command).catch(function(error) {
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

function updateTelemetry(cpuPercent, ramString, ramPercent) {
    document.getElementById('cpu-val').innerText = `${cpuPercent}%`;
    document.getElementById('cpu-bar').style.width = `${cpuPercent}%`;

    document.getElementById('ram-val').innerText = ramString;
    document.getElementById('ram-bar').style.width = `${ramPercent}%`;
}

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
    if (coordsEl) coordsEl.innerText = `${x}, ${y}`;
}