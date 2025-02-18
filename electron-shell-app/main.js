const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

let mainWindow;
let shell;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false, // For simplicity in this example
        },
    });

    mainWindow.loadFile('index.html');
}

function getDefaultShell() {
    if (os.platform() === 'win32') {
        return process.env.ComSpec || 'powershell.exe';  // CMD or PowerShell on Windows
    } else {
        return process.env.SHELL || '/bin/bash';  // Bash/Zsh on Linux/macOS
    }
}

// Handle incoming command requests from renderer
ipcMain.on('send-command', (event, command) => {
    if (shell) {
        shell.stdin.write(command + '\n');
    }
});

ipcMain.on('request-completion', (event, partial) => {
    const shellPath = getDefaultShell();
    
    // Different completion commands based on shell type
    let completionCommand;
    if (shellPath.includes('bash')) {
        completionCommand = `compgen -c "${partial}"`;
    } else if (shellPath.includes('zsh')) {
        completionCommand = `print -rl -- ${partial}*(N)`;
    } else if (shellPath.includes('powershell')) {
        // PowerShell tab completion is more complex and might need a different approach
        completionCommand = `Get-Command "${partial}*" | Select-Object -ExpandProperty Name`;
    } else {
        // Default to basic command completion
        completionCommand = `compgen -c "${partial}"`;
    }

    exec(completionCommand, (error, stdout, stderr) => {
        if (!error) {
            const completions = stdout.trim().split('\n').filter(Boolean);
            event.reply('completion-results', completions);
        }
    });
});

// Create a persistent shell process
function startShell() {
    const shellPath = getDefaultShell();
    shell = spawn(shellPath, [], { shell: true });

    // Capture shell output and send it to renderer
    shell.stdout.on('data', (data) => {
        mainWindow.webContents.send('shell-output', data.toString());
    });

    shell.stderr.on('data', (data) => {
        mainWindow.webContents.send('shell-output', `Error: ${data}`);
    });

    shell.on('close', (code) => {
        console.log(`Shell exited with code ${code}`);
    });
}

app.whenReady().then(() => {
    createWindow();
    startShell();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
