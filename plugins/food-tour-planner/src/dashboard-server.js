/* Dashboard server - serves generated HTML reports on port 3002. */

const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const port = process.env.DASHBOARD_PORT || 3002;
const dashboardDir = path.join(__dirname, '..', 'dashboards');

// Ensure dashboards directory exists
if (!fs.existsSync(dashboardDir)) {
  fs.mkdirSync(dashboardDir, { recursive: true });
}

// Serve static files from dashboards directory
app.use(express.static(dashboardDir));

// List all available dashboards
app.get('/api/dashboards', (req, res) => {
  try {
    const files = fs.readdirSync(dashboardDir)
      .filter(file => file.endsWith('.html'))
      .map(file => ({
        filename: file,
        name: file.replace('.html', '').replace(/_/g, ' '),
        url: `http://localhost:${port}/${file}`,
        created: fs.statSync(path.join(dashboardDir, file)).mtime
      }))
      .sort((a, b) => b.created - a.created);
    
    res.json(files);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Home page listing all dashboards
app.get('/', (req, res) => {
  try {
    const files = fs.readdirSync(dashboardDir)
      .filter(file => file.endsWith('.html'))
      .map(file => ({
        filename: file,
        name: file.replace('.html', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        created: fs.statSync(path.join(dashboardDir, file)).mtime
      }))
      .sort((a, b) => b.created - a.created);
    
    const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Food Tour Dashboards</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 42px;
            color: #667eea;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 18px;
        }
        .dashboards {
            display: grid;
            gap: 20px;
        }
        .dashboard-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none;
            color: inherit;
            display: block;
        }
        .dashboard-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }
        .dashboard-card h2 {
            font-size: 24px;
            color: #333;
            margin-bottom: 10px;
        }
        .dashboard-card .meta {
            color: #999;
            font-size: 14px;
        }
        .empty-state {
            background: white;
            padding: 60px;
            border-radius: 16px;
            text-align: center;
            color: #999;
        }
        .empty-state-icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗺️ Food Tour Dashboards</h1>
            <p>AI-Generated Food Tour Reports</p>
        </div>
        
        <div class="dashboards">
            ${files.length === 0 ? `
                <div class="empty-state">
                    <div class="empty-state-icon">📋</div>
                    <h2>No dashboards yet</h2>
                    <p>Create a food tour plan to generate your first dashboard</p>
                </div>
            ` : files.map(file => `
                <a href="/${file.filename}" class="dashboard-card">
                    <h2>🍽️ ${file.name}</h2>
                    <div class="meta">Created ${new Date(file.created).toLocaleString()}</div>
                </a>
            `).join('')}
        </div>
    </div>
</body>
</html>
    `;
    
    res.send(html);
  } catch (error) {
    res.status(500).send(`Error: ${error.message}`);
  }
});

app.listen(port, () => {
  console.log(`\n🗺️ Dashboard Server`);
  console.log(`=`.repeat(50));
  console.log(`Server running on http://localhost:${port}`);
  console.log(`Serving dashboards from: ${dashboardDir}`);
  console.log(`=`.repeat(50) + '\n');
});

