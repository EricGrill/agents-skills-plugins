#!/usr/bin/env node
/**
 * Plugin Update Checker
 * 
 * Checks for available plugin updates and notifies users
 * Usage: node update-checker.js [options]
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const REGISTRY_URL = 'https://raw.githubusercontent.com/EricGrill/agents-skills-plugins/main/';
const LOCAL_PLUGIN_DIR = process.env.CLAUDE_PLUGINS_DIR || path.join(require('os').homedir(), '.claude', 'plugins');
const CACHE_FILE = path.join(LOCAL_PLUGIN_DIR, '.update-cache.json');
const CHECK_INTERVAL = 24 * 60 * 60 * 1000; // 24 hours

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function colorize(text, color) {
  return `${colors[color]}${text}${colors.reset}`;
}

class UpdateChecker {
  constructor() {
    this.cache = this.loadCache();
    this.updates = [];
    this.breakingChanges = [];
  }

  loadCache() {
    try {
      if (fs.existsSync(CACHE_FILE)) {
        return JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
      }
    } catch (e) {
      // Ignore cache errors
    }
    return { lastCheck: 0, plugins: {} };
  }

  saveCache() {
    try {
      if (!fs.existsSync(LOCAL_PLUGIN_DIR)) {
        fs.mkdirSync(LOCAL_PLUGIN_DIR, { recursive: true });
      }
      fs.writeFileSync(CACHE_FILE, JSON.stringify(this.cache, null, 2));
    } catch (e) {
      console.error('Failed to save cache:', e.message);
    }
  }

  shouldCheck() {
    const now = Date.now();
    return (now - this.cache.lastCheck) > CHECK_INTERVAL;
  }

  async fetchRegistryIndex() {
    return new Promise((resolve, reject) => {
      const url = `${REGISTRY_URL}plugins-index.json`;
      https.get(url, (res) => {
        if (res.statusCode !== 200) {
          reject(new Error(`HTTP ${res.statusCode}`));
          return;
        }
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(e);
          }
        });
      }).on('error', reject);
    });
  }

  getInstalledPlugins() {
    const plugins = [];
    try {
      if (fs.existsSync(LOCAL_PLUGIN_DIR)) {
        const entries = fs.readdirSync(LOCAL_PLUGIN_DIR, { withFileTypes: true });
        for (const entry of entries) {
          if (entry.isDirectory() && !entry.name.startsWith('.')) {
            const manifestPath = path.join(LOCAL_PLUGIN_DIR, entry.name, 'plugin.json');
            if (fs.existsSync(manifestPath)) {
              const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
              plugins.push({
                name: entry.name,
                version: manifest.version,
                manifest: manifest
              });
            }
          }
        }
      }
    } catch (e) {
      console.error('Error reading installed plugins:', e.message);
    }
    return plugins;
  }

  compareVersions(current, latest) {
    const parts1 = current.split('.').map(Number);
    const parts2 = latest.split('.').map(Number);
    
    for (let i = 0; i < Math.max(parts1.length, parts2.length); i++) {
      const a = parts1[i] || 0;
      const b = parts2[i] || 0;
      if (a < b) return -1;
      if (a > b) return 1;
    }
    return 0;
  }

  parseChangelog(changelog) {
    const breaking = [];
    if (!changelog) return breaking;
    
    const lines = changelog.split('\n');
    let inBreakingSection = false;
    
    for (const line of lines) {
      if (line.match(/#{1,3}\s*(breaking|⚠️)/i)) {
        inBreakingSection = true;
      } else if (line.match(/^#{1,3}\s/) && inBreakingSection) {
        inBreakingSection = false;
      } else if (inBreakingSection && line.trim().startsWith('-')) {
        breaking.push(line.trim().substring(1).trim());
      }
    }
    
    return breaking;
  }

  async checkForUpdates() {
    console.log(colorize('🔍 Checking for plugin updates...', 'cyan'));
    
    try {
      const registry = await this.fetchRegistryIndex();
      const installed = this.getInstalledPlugins();
      
      this.updates = [];
      this.breakingChanges = [];
      
      for (const plugin of installed) {
        const registryPlugin = registry.plugins[plugin.name];
        if (!registryPlugin) continue;
        
        const comparison = this.compareVersions(plugin.version, registryPlugin.version);
        if (comparison < 0) {
          const isMajorBump = registryPlugin.version.split('.')[0] !== plugin.version.split('.')[0];
          
          const updateInfo = {
            name: plugin.name,
            currentVersion: plugin.version,
            latestVersion: registryPlugin.version,
            isMajorBump,
            quality: registryPlugin.quality,
            changelog: null
          };
          
          // Check for breaking changes
          if (isMajorBump) {
            this.breakingChanges.push(updateInfo);
          }
          
          this.updates.push(updateInfo);
        }
      }
      
      this.cache.lastCheck = Date.now();
      this.saveCache();
      
      return this.updates;
    } catch (e) {
      console.error(colorize(`❌ Failed to check for updates: ${e.message}`, 'red'));
      return [];
    }
  }

  formatUpdate(update) {
    const name = colorize(update.name, 'bright');
    const current = colorize(update.currentVersion, 'red');
    const latest = colorize(update.latestVersion, 'green');
    const badge = update.quality ? colorize(`[${update.quality}]`, 'yellow') : '';
    
    return `  ${name} ${badge}: ${current} → ${latest}`;
  }

  displayResults() {
    if (this.updates.length === 0) {
      console.log(colorize('\n✅ All plugins are up to date!', 'green'));
      return;
    }
    
    console.log(colorize(`\n📦 ${this.updates.length} update(s) available:\n`, 'bright'));
    
    for (const update of this.updates) {
      console.log(this.formatUpdate(update));
    }
    
    if (this.breakingChanges.length > 0) {
      console.log(colorize('\n⚠️  Breaking changes detected in:', 'red'));
      for (const update of this.breakingChanges) {
        console.log(`  - ${update.name} (${update.currentVersion} → ${update.latestVersion})`);
      }
      console.log(colorize('\n  Review changelogs before updating: /plugin changelog <name>', 'yellow'));
    }
    
    console.log(colorize('\n💡 Commands:', 'cyan'));
    console.log('  /plugin update          Update all plugins');
    console.log('  /plugin update <name>   Update specific plugin');
    console.log('  /plugin list --updates  List only plugins with updates');
  }

  async run() {
    const args = process.argv.slice(2);
    
    if (args.includes('--help') || args.includes('-h')) {
      console.log(`
${colorize('Plugin Update Checker', 'bright')}

Usage: node update-checker.js [options]

Options:
  --force, -f       Force check even if cache is fresh
  --json, -j        Output results as JSON
  --quiet, -q       Only show updates (no status messages)
  --help, -h        Show this help message

Environment Variables:
  CLAUDE_PLUGINS_DIR    Plugin installation directory
      `);
      return;
    }
    
    const force = args.includes('--force') || args.includes('-f');
    const json = args.includes('--json') || args.includes('-j');
    const quiet = args.includes('--quiet') || args.includes('-q');
    
    if (!quiet && !json) {
      console.log(colorize('╔════════════════════════════════════╗', 'blue'));
      console.log(colorize('║   Claude Code Plugin Update Check  ║', 'blue'));
      console.log(colorize('╚════════════════════════════════════╝', 'blue'));
    }
    
    if (!force && !this.shouldCheck() && !json) {
      if (!quiet) {
        console.log(colorize('\nℹ️  Checked recently. Use --force to check again.', 'yellow'));
      }
      return;
    }
    
    await this.checkForUpdates();
    
    if (json) {
      console.log(JSON.stringify({
        updates: this.updates,
        breakingChanges: this.breakingChanges,
        hasUpdates: this.updates.length > 0,
        timestamp: new Date().toISOString()
      }, null, 2));
    } else {
      this.displayResults();
    }
  }
}

// Run if called directly
if (require.main === module) {
  const checker = new UpdateChecker();
  checker.run().catch(e => {
    console.error(colorize(`Fatal error: ${e.message}`, 'red'));
    process.exit(1);
  });
}

module.exports = UpdateChecker;
