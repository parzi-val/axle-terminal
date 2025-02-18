// renderer.js
const { ipcRenderer } = require('electron');

const input = document.getElementById('command-input');
const output = document.getElementById('terminal-output');

let currentCompletions = [];
let completionIndex = -1;

const escapeHTML = (str) => str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');


// Send commands to the main process
input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const command = input.value;
        ipcRenderer.send('send-command', command);
        input.value = '';
        currentCompletions = [];
        completionIndex = -1;
    }
});

// Handle tab completion
input.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        e.preventDefault();
        
        if (currentCompletions.length === 0) {
            // First tab press - request completions
            const inputValue = input.value;
            ipcRenderer.send('request-completion', inputValue);
        } else {
            // Subsequent tab presses - cycle through completions
            completionIndex = (completionIndex + 1) % currentCompletions.length;
            const completion = currentCompletions[completionIndex];
            input.value = completion;
        }
    } else {
        // Reset completions on any other key
        currentCompletions = [];
        completionIndex = -1;
    }
});

// Listen for completion suggestions
ipcRenderer.on('completion-results', (event, completions) => {
    if (completions && completions.length > 0) {
        currentCompletions = completions;
        completionIndex = 0;
        input.value = completions[0];
    }
});

// Listen for shell output
ipcRenderer.on('shell-output', (event, data) => {
    if (data.includes('<<HR>>')) {
        output.innerHTML += '<hr class="solid">';
    } else if (data.includes('clear')) {
        output.innerHTML = '';
    } else {
       
        output.innerHTML += `<div>${escapeHTML(data)}</div>`;
        output.scrollTop = output.scrollHeight;
    }
});