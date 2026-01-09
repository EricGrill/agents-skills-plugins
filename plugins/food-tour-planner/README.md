# DeepAgent Food Tours

AI-powered food tour planner using [LangChain DeepAgents](https://github.com/langchain-ai/deepagents), Google Maps API, and Tavily research.

## Screenshots

### Interactive Map Interface
<img src="screenshots/Screenshot%202025-11-05%20at%2012.32.22%E2%80%AFAM.png" width="800" alt="Map interface with search points">

### DeepAgent Planning Process
<img src="screenshots/Screenshot%202025-11-05%20at%2012.47.05%E2%80%AFAM.png" width="800" alt="Adding search points to the map">
<img src="screenshots/Screenshot%202025-11-05%20at%2012.48.38%E2%80%AFAM.png" width="800" alt="Natural language AI prompt">
<img src="screenshots/Screenshot%202025-11-05%20at%2012.49.23%E2%80%AFAM.png" width="800" alt="AI agents planning the tour">
<img src="screenshots/Screenshot%202025-11-05%20at%2012.50.43%E2%80%AFAM.png" width="800" alt="Reviews and neighborhood insights">


### Generated Tour Dashboard
<img src="screenshots/Screenshot%202025-11-05%20at%2012.49.50%E2%80%AFAM.png" width="800" alt="Beautiful HTML tour dashboard header">
<img src="screenshots/Screenshot%202025-11-05%20at%2012.50.06%E2%80%AFAM.png" width="800" alt="Establishment details with photos and reviews">
<img src="screenshots/Screenshot%202025-11-05%20at%2012.50.14%E2%80%AFAM.png" width="800" alt="Personalized tour recommendations">


## Features

- **Interactive Map Interface**: Click to add search points and visualize coverage areas
- **Smart Search**: Scan neighborhoods with multiple overlapping search radii for complete coverage
- **AI Planning**: Use natural language prompts to let AI plan personalized food tours
- **Lightweight Data Collection**: Efficient API usage with minimal requests
- **Beautiful Dashboards**: Auto-generated HTML reports with establishment details and research findings
- **Flexible Export**: Preview results and select only the establishments you want before detailed export

## Architecture

The project uses a multi-agent architecture powered by LangChain DeepAgents:

- **Scan Manager** (Node.js): Web UI and basic scan functionality
- **Dashboard Server** (Node.js): Serves generated HTML tour reports
- **DeepAgent API** (Python): Coordinates AI agents for intelligent tour planning
  - **Restaurant Finder Agent**: Searches and evaluates food establishments
  - **Neighborhood Researcher Agent**: Analyzes local culture and food trends
  - **Dashboard Creator Agent**: Generates beautiful HTML reports

## Prerequisites

- **Node.js** >= 18.0.0
- **Python** >= 3.9
- **npm** >= 9.0.0

## API Keys Required

1. **Google Maps API Key** ([Get it here](https://console.cloud.google.com/google/maps-apis))
   - Enable: Places API, Geocoding API, Maps JavaScript API
   
2. **Tavily API Key** ([Get it here](https://tavily.com))
   - For neighborhood research and web data
   
3. **Anthropic API Key** ([Get it here](https://console.anthropic.com)) OR **OpenAI API Key** ([Get it here](https://platform.openai.com))
   - For AI agent reasoning

## Installation

1. Clone the repository:
```bash
git clone https://github.com/muratcankoylan/deepagent-food-tours.git
cd deepagent-food-tours
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

4. Create `.env` file from template:
```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys:
```bash
GOOGLE_MAPS_API_KEY=your_actual_key_here
TAVILY_API_KEY=your_actual_key_here
ANTHROPIC_API_KEY=your_actual_key_here  # or OPENAI_API_KEY
```

## Usage

### Quick Start

Run all three services at once:
```bash
./start.sh
```

This will start:
- Scan Manager UI: http://localhost:3001
- Dashboard Server: http://localhost:3002
- DeepAgent API: http://localhost:5001

### Manual Start (Individual Services)

If you prefer to run services individually:

```bash
# Terminal 1: Scan Manager
npm start

# Terminal 2: Dashboard Server
npm run dashboard-server

# Terminal 3: DeepAgent API
npm run deepagent-api
```

### Basic Scan (No AI)

1. Open http://localhost:3001
2. Click on the map to add search points
3. Configure radius and categories
4. Click "Create Scan Task"
5. Wait for scanning to complete
6. Click "View Results & Export"
7. Select establishments and export

### AI-Powered Tour Planning

1. Open http://localhost:3001
2. Click on the map to add search points for the neighborhood
3. Enter an AI prompt like:
   - "I want a fun evening exploring local food"
   - "Plan a romantic dinner date in this area"
   - "Find the best brunch spots for a Sunday morning"
4. Click "Create Scan Task"
5. Wait 1-2 minutes for the AI to plan your tour
6. Click "View AI Dashboard" to see the generated tour report

## Project Structure

```
deepagent-food-tours/
├── src/
│   ├── services/
│   │   ├── places.js                    # Google Places API wrapper
│   │   ├── neighborhood-analyzer.js     # Multi-point scan logic
│   │   └── geographic-sorter.js         # Route optimization
│   ├── agents/
│   │   ├── food_tour_agent.py           # Main DeepAgent
│   │   └── tools/
│   │       ├── places_lightweight.py    # Lightweight Places API
│   │       ├── tavily_research.py       # Neighborhood research
│   │       └── dashboard_generator.py   # HTML report generator
│   ├── scan-manager.js                  # Web UI backend
│   ├── dashboard-server.js              # Dashboard hosting
│   └── deepagent-api.py                 # Python API bridge
├── public/
│   └── index.html                       # Web UI frontend
├── dashboards/                          # Generated HTML reports
├── output/                              # Export JSON files
├── package.json
├── requirements.txt
├── start.sh
└── .env.example
```

## How It Works

### Basic Scanning

1. User adds search points on the map
2. System performs circular searches at each point
3. Automatic deduplication removes overlapping results
4. User previews results and selects items for detailed export
5. Full details fetched only for selected items (saves API calls)

### AI-Powered Planning

1. User provides location and natural language prompt
2. DeepAgent creates task breakdown
3. Restaurant Finder agent searches for relevant establishments
4. Neighborhood Researcher agent analyzes the area
5. Dashboard Creator agent generates an HTML report
6. User views the complete tour plan at http://localhost:3002


## Troubleshooting

### Port Already in Use

If you see "address already in use" errors:
```bash
# Kill processes on ports 3001, 3002, 5001
lsof -ti:3001,3002,5001 | xargs kill -9
```

### Python Import Errors

Make sure you're in the project root when running:
```bash
cd /path/to/deepagent-food-tours
python3 src/deepagent-api.py
```

### Missing API Keys

Check your `.env` file has all required keys:
```bash
cat .env
```

### DeepAgent Timeout

For large neighborhoods, increase the timeout in `src/scan-manager.js` (currently 5 minutes).

## Contributing

Contributions welcome. Please open an issue first to discuss proposed changes.

## License

MIT

## Acknowledgments

- Built with [LangChain DeepAgents](https://github.com/langchain-ai/deepagents)
- Uses Google Maps Platform APIs
- Powered by Tavily Research API

Feel free to use this as a template for your own DeepAgent projects.

