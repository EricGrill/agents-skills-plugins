#!/usr/bin/env node

/**
 * NPX launcher for MCP Multi-Agent SSH
 *
 * This script ensures Python 3.10+ is available, sets up a virtual environment,
 * installs the Python package, and launches the MCP server.
 */

const { spawn, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const CONFIG_DIR = path.join(os.homedir(), '.mcp-multi-agent-ssh');
const VENV_DIR = path.join(CONFIG_DIR, 'venv');
const PACKAGE_DIR = path.dirname(__dirname);

function log(message) {
    console.error(`[mcp-multi-agent-ssh] ${message}`);
}

function checkPython() {
    const pythonCmds = ['python3', 'python'];

    for (const cmd of pythonCmds) {
        try {
            const version = execFileSync(cmd, ['--version'], { encoding: 'utf8' });
            const match = version.match(/Python (\d+)\.(\d+)/);
            if (match) {
                const major = parseInt(match[1]);
                const minor = parseInt(match[2]);
                if (major >= 3 && minor >= 10) {
                    return cmd;
                }
            }
        } catch (e) {
            // Command not found, try next
        }
    }

    return null;
}

function ensureConfigDir() {
    if (!fs.existsSync(CONFIG_DIR)) {
        fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
    }
}

function venvExists() {
    const venvPython = process.platform === 'win32'
        ? path.join(VENV_DIR, 'Scripts', 'python.exe')
        : path.join(VENV_DIR, 'bin', 'python');
    return fs.existsSync(venvPython);
}

function getVenvPython() {
    return process.platform === 'win32'
        ? path.join(VENV_DIR, 'Scripts', 'python.exe')
        : path.join(VENV_DIR, 'bin', 'python');
}

function getVenvPip() {
    return process.platform === 'win32'
        ? path.join(VENV_DIR, 'Scripts', 'pip.exe')
        : path.join(VENV_DIR, 'bin', 'pip');
}

function createVenv(pythonCmd) {
    log('Creating virtual environment...');
    execFileSync(pythonCmd, ['-m', 'venv', VENV_DIR], { stdio: 'inherit' });
}

function installPackage() {
    log('Installing mcp-multi-agent-ssh...');
    const pip = getVenvPip();
    execFileSync(pip, ['install', '-e', PACKAGE_DIR], { stdio: 'inherit' });
}

function isPackageInstalled() {
    const pip = getVenvPip();
    try {
        execFileSync(pip, ['show', 'mcp-multi-agent-ssh'], { encoding: 'utf8', stdio: 'pipe' });
        return true;
    } catch (e) {
        return false;
    }
}

function runServer() {
    const venvPython = getVenvPython();

    // Spawn the Python server, forwarding stdio for MCP communication
    const server = spawn(venvPython, ['-m', 'mcp_multi_agent_ssh.server'], {
        stdio: ['inherit', 'inherit', 'inherit'],
        env: { ...process.env }
    });

    server.on('close', (code) => {
        process.exit(code || 0);
    });

    server.on('error', (err) => {
        log(`Failed to start server: ${err.message}`);
        process.exit(1);
    });

    // Handle termination signals
    process.on('SIGINT', () => {
        server.kill('SIGINT');
    });
    process.on('SIGTERM', () => {
        server.kill('SIGTERM');
    });
}

async function main() {
    // Check Python version
    const pythonCmd = checkPython();
    if (!pythonCmd) {
        log('Error: Python 3.10+ is required but not found.');
        log('Please install Python 3.10 or later from https://www.python.org/');
        process.exit(1);
    }

    // Ensure config directory exists
    ensureConfigDir();

    // Create venv if needed
    if (!venvExists()) {
        createVenv(pythonCmd);
    }

    // Install package if needed
    if (!isPackageInstalled()) {
        installPackage();
    }

    // Run the server
    runServer();
}

main().catch((err) => {
    log(`Error: ${err.message}`);
    process.exit(1);
});
