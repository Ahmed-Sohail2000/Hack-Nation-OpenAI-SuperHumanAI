# How to Run the AI Chief of Staff App

## Quick Start Guide

### Step 1: Verify Your Setup

Make sure you have:
- ✅ Neo4j AuraDB credentials in `.env` file
- ✅ OpenAI API key in `.env` file
- ✅ `emails.json` file (created from `process_emails.py`)

### Step 2: Load Data into Neo4j (First Time Only)

If you haven't loaded your email data into Neo4j yet:

```bash
python load_graph_data.py
```

This will:
- Connect to your Neo4j AuraDB
- Load all emails from `emails.json`
- Create the communication network graph
- Take a few minutes depending on data size

**Note:** You only need to do this once, or when you have new email data.

### Step 3: Start the Web Server

Open a terminal/command prompt in the project folder and run:

```bash
python run_api.py
```

You should see:
```
Neo4j connection established
Starting AI Chief of Staff API on http://localhost:8000
 * Serving Flask app 'src.api'
 * Debug mode: on
 * Running on http://127.0.0.1:8000
```

### Step 4: Open in Your Browser

Once the server is running:

1. Open your web browser (Chrome, Firefox, Edge, etc.)
2. Go to: **http://localhost:8000**
3. You should see the AI Chief of Staff interface!

### Step 5: Explore the Interface

The web interface has three tabs:

1. **Query AI** - Ask questions about your organization
2. **Communication Graph** - Visualize the communication network
3. **Insights** - View organizational statistics

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "Neo4j not initialized" error
- Check your `.env` file has correct Neo4j credentials
- Make sure your AuraDB instance is running
- Test connection: `python -c "from src.neo4j_graph import Neo4jGraphDB; db = Neo4jGraphDB(); print('Connected!'); db.close()"`

### "emails.json not found"
```bash
python process_emails.py
```

### Port already in use
Change port in `.env`: `PORT=8001` (or any other port)

### Can't connect to Neo4j
- Verify your AuraDB instance is active in the console
- Check your URI uses `neo4j+s://` format
- Double-check username and password

## What You'll See

### Query AI Tab
- Enter questions like:
  - "Who are the top communicators?"
  - "What are the main topics discussed?"
  - "Analyze communication patterns"

### Communication Graph Tab
- Interactive network visualization
- Click "Load Graph" to see the network
- Drag nodes, zoom, and explore relationships
- Click nodes to see details

### Insights Tab
- Total emails count
- Unique senders/receivers
- Network statistics

## Stopping the Server

Press `Ctrl+C` in the terminal to stop the server.

## Next Steps

- Try different queries in the Query AI tab
- Explore the communication graph
- Analyze specific people's networks
- Use the REST API for programmatic access

Enjoy exploring your organizational intelligence! 🚀
