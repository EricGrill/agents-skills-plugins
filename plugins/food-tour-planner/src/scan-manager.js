const express = require('express');
const path = require('path');
const NeighborhoodAnalyzer = require('./services/neighborhood-analyzer');
const fs = require('fs');

require('dotenv').config();

const app = express();
const port = process.env.PORT || 3001;

app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'public')));

// Store active scan tasks
const activeTasks = new Map();
let taskIdCounter = 0;

// Get API key (sanitized for frontend)
app.get('/api/config', (req, res) => {
  res.json({
    googleMapsApiKey: process.env.GOOGLE_MAPS_API_KEY || '',
  });
});

// Create a new scan task
app.post('/api/tasks', async (req, res) => {
  const { name, searchPoints, radius, types, aiPrompt } = req.body;

  if (!searchPoints || !Array.isArray(searchPoints) || searchPoints.length === 0) {
    return res.status(400).json({ error: 'searchPoints array is required' });
  }

  const taskId = ++taskIdCounter;
  const task = {
    id: taskId,
    name: name || `Scan ${taskId}`,
    searchPoints,
    radius: radius || 200,
    types: types || ['restaurant', 'cafe', 'bar', 'bakery', 'meal_takeaway'],
    aiPrompt: aiPrompt || null,
    status: 'pending',
    createdAt: new Date().toISOString(),
    progress: {
      current: 0,
      total: searchPoints.length,
      establishments: 0,
    },
    preview: null,
    selectedForExport: [],
  };

  activeTasks.set(taskId, task);

  // Check if AI prompt exists - use DeepAgent or basic scan
  if (aiPrompt && aiPrompt.trim().length > 0) {
    console.log(`\n🤖 AI Task detected: ${name}`);
    console.log(`Prompt: ${aiPrompt}`);
    startAITask(taskId);
  } else {
    console.log(`\n📊 Basic scan task: ${name}`);
    startPreviewScan(taskId);
  }

  res.json({
    success: true,
    taskId,
    task,
  });
});

// Export selected establishments with full details
app.post('/api/tasks/:taskId/export', async (req, res) => {
  const taskId = parseInt(req.params.taskId);
  const { selectedIds } = req.body;

  const task = activeTasks.get(taskId);
  if (!task) {
    return res.status(404).json({ error: 'Task not found' });
  }

  if (!task.preview || !task.preview.establishments) {
    return res.status(400).json({ error: 'No preview data available' });
  }

  task.selectedForExport = selectedIds || [];
  task.status = 'exporting';

  startDetailedExport(taskId);

  res.json({
    success: true,
    message: `Exporting ${selectedIds.length} establishments`,
  });
});

// Get task status
app.get('/api/tasks/:taskId', (req, res) => {
  const taskId = parseInt(req.params.taskId);
  const task = activeTasks.get(taskId);

  if (!task) {
    return res.status(404).json({ error: 'Task not found' });
  }

  res.json(task);
});

// Get all tasks
app.get('/api/tasks', (req, res) => {
  const tasks = Array.from(activeTasks.values());
  res.json(tasks);
});

// Delete task
app.delete('/api/tasks/:taskId', (req, res) => {
  const taskId = parseInt(req.params.taskId);
  
  if (!activeTasks.has(taskId)) {
    return res.status(404).json({ error: 'Task not found' });
  }

  activeTasks.delete(taskId);
  res.json({ success: true });
});

// Start AI-powered task using DeepAgent
async function startAITask(taskId) {
  const task = activeTasks.get(taskId);
  if (!task) return;

  task.status = 'ai-planning';
  
  try {
    console.log(`\n🧠 Calling DeepAgent API...`);
    
    // Get center point from search points
    const centerLat = task.searchPoints.reduce((sum, p) => sum + p.lat, 0) / task.searchPoints.length;
    const centerLng = task.searchPoints.reduce((sum, p) => sum + p.lng, 0) / task.searchPoints.length;
    
    // Call DeepAgent API
    const axios = require('axios');
    const response = await axios.post('http://localhost:5001/plan-tour', {
      location_name: task.name,
      coordinates: { lat: centerLat, lng: centerLng },
      user_prompt: task.aiPrompt,
      search_points: task.searchPoints
    }, {
      timeout: 300000 // 5 minutes timeout
    });
    
    console.log(`✅ DeepAgent completed!`);
    
    task.status = 'completed';
    task.completedAt = new Date().toISOString();
    task.aiResult = response.data.result;
    task.dashboardUrl = response.data.dashboard_url;
    
    console.log(`📊 Dashboard available at: ${task.dashboardUrl}`);
    
  } catch (error) {
    console.error(`❌ DeepAgent error:`, error.message);
    if (error.response) {
      console.error(`Response status: ${error.response.status}`);
      console.error(`Response data:`, error.response.data);
    } else if (error.request) {
      console.error(`No response received. Request was made but no response.`);
    } else {
      console.error(`Error details:`, error);
    }
    task.status = 'error';
    task.error = `DeepAgent API error: ${error.message}. Make sure the DeepAgent server is running on port 5001.`;
  }
}

// Start preview scan (basic info only, no Place Details API calls)
async function startPreviewScan(taskId) {
  const task = activeTasks.get(taskId);
  if (!task) return;

  task.status = 'scanning';
  const analyzer = new NeighborhoodAnalyzer(process.env.GOOGLE_MAPS_API_KEY);

  try {
    // Scan all points (only Places Nearby API, no details)
    const places = await analyzer.analyzeNeighborhood(
      task.searchPoints,
      {
        radius: task.radius,
        types: task.types,
      }
    );

    task.progress.establishments = places.length;
    task.status = 'preview-ready';
    
    // Store preview data
    task.preview = {
      establishments: places.map(place => ({
        placeId: place.place_id,
        name: place.name,
        address: place.vicinity || place.formatted_address,
        location: place.geometry.location,
        rating: place.rating,
        totalReviews: place.user_ratings_total || 0,
        priceLevel: place.price_level ? '$'.repeat(place.price_level) : null,
        types: place.types,
        isOpen: place.opening_hours?.open_now,
      })),
      totalFound: places.length,
      analyzedAt: new Date().toISOString(),
    };

  } catch (error) {
    task.status = 'error';
    task.error = error.message;
  }
}

// Export selected establishments with full details
async function startDetailedExport(taskId) {
  const task = activeTasks.get(taskId);
  if (!task) return;

  const analyzer = new NeighborhoodAnalyzer(process.env.GOOGLE_MAPS_API_KEY);

  try {
    // Get only selected establishments
    const selectedEstablishments = task.preview.establishments
      .filter(e => task.selectedForExport.includes(e.placeId));

    // Deduplicate
    const uniqueMap = new Map();
    selectedEstablishments.forEach(e => {
      uniqueMap.set(e.placeId, e);
    });

    console.log(`\nExporting ${uniqueMap.size} unique establishments (${selectedEstablishments.length - uniqueMap.size} duplicates removed)`);

    // Convert to format expected by getDetailedData
    const placesToExport = Array.from(uniqueMap.values()).map(e => ({
      place_id: e.placeId,
      name: e.name,
      vicinity: e.address,
      geometry: { location: e.location },
    }));

    // Get detailed data
    const establishments = await analyzer.getDetailedData(placesToExport);

    // Final deduplication check
    const finalUnique = new Map();
    establishments.forEach(est => {
      finalUnique.set(est.placeId, est);
    });

    const finalEstablishments = Array.from(finalUnique.values());

    task.status = 'completed';
    task.completedAt = new Date().toISOString();
    task.results = {
      totalEstablishments: finalEstablishments.length,
      establishments: finalEstablishments,
      deduplicationStats: {
        originalCount: selectedEstablishments.length,
        duplicatesRemoved: selectedEstablishments.length - finalEstablishments.length,
        finalUniqueCount: finalEstablishments.length,
      },
      sorted: {
        byHighestRating: finalEstablishments
          .filter(e => e.totalReviews >= 10)
          .sort((a, b) => (b.rating || 0) - (a.rating || 0)),
        
        byMostReviewed: [...finalEstablishments]
          .sort((a, b) => b.totalReviews - a.totalReviews),
        
        hiddenGems: finalEstablishments
          .filter(e => (e.rating || 0) >= 4.5 && e.totalReviews < 100 && e.totalReviews >= 5)
          .sort((a, b) => (b.rating || 0) - (a.rating || 0)),
        
        crowdFavorites: finalEstablishments
          .filter(e => (e.rating || 0) >= 4.3 && e.totalReviews >= 500)
          .sort((a, b) => b.totalReviews - a.totalReviews),
      },
    };

    // Save to file
    const outputDir = path.join(__dirname, '..', 'output');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `export-${taskId}-${timestamp}.json`;
    const filepath = path.join(outputDir, filename);

    fs.writeFileSync(filepath, JSON.stringify(task.results, null, 2));
    task.outputFile = filename;

    console.log(`\n✓ Export complete: ${finalEstablishments.length} unique establishments`);
    console.log(`✓ Saved to: ${filename}`);

  } catch (error) {
    task.status = 'error';
    task.error = error.message;
  }
}

// Serve main UI
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'index.html'));
});

app.listen(port, () => {
  console.log(`\n${'='.repeat(70)}`);
  console.log('DeepAgent Food Tour Scanner');
  console.log('='.repeat(70));
  console.log(`\n🚀 Server running at: http://localhost:${port}`);
  console.log(`📍 Open in browser to create scan tasks\n`);
  console.log('='.repeat(70) + '\n');
});

