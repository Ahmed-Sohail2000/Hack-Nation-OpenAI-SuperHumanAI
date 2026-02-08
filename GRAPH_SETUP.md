# Neo4j Graph Visualization Setup Guide

## Quick Start

### 1. Set Up Neo4j AuraDB (Cloud)

**Neo4j AuraDB Setup (Recommended for Cloud/Production)**
1. Sign up for a free account at https://neo4j.com/cloud/aura/
2. Click "Create Database" → "Free Instance"
3. Choose a database name and region
4. Wait for the database to be created (takes 2-3 minutes)
5. Once created, click on your database
6. You'll see connection details:
   - **Connection URI**: `neo4j+s://xxxxx.databases.neo4j.io`
   - **Username**: Usually `neo4j`
   - **Password**: Click "Show Password" to reveal it (save this!)
   - **Database Name**: Usually `neo4j`

**Important Notes:**
- The URI uses `neo4j+s://` (secure connection) not `bolt://`
- Save your password immediately - you won't be able to see it again
- Free tier includes: 50K nodes, 175K relationships, 0.5GB storage

### 2. Configure .env File

Add your Neo4j AuraDB credentials to your `.env` file:

```env
# Neo4j AuraDB Configuration
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_aura_password_here
```

**Example:**
```env
NEO4J_URI=neo4j+s://a1b2c3d4.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=MySecurePassword123!
```

**Where to find your credentials:**
1. Log into https://console.neo4j.io/
2. Select your database instance
3. Click "Connection Details" or "Connect"
4. Copy the URI, username, and password

### 3. Load Data into Neo4j

Run the data loader script:

```bash
python load_graph_data.py
```

This will:
- Load all emails from `emails.json`
- Create Person nodes for each email address
- Create COMMUNICATED_WITH relationships between people
- Track communication counts and subjects

### 4. Access the Graph Visualization

1. Start the API server:
   ```bash
   python run_api.py
   ```

2. Open your browser to `http://localhost:5000`

3. Click on the "Communication Graph" tab

4. Click "Load Graph" to visualize the network

## Graph Features

- **Interactive Visualization**: Drag nodes, zoom, pan
- **Node Sizing**: Larger nodes = more communications
- **Edge Thickness**: Thicker edges = more communications between people
- **Click Nodes**: View details about specific people
- **View Person Network**: Click "View Network" to see a person's connections
- **Adjustable Limits**: Change the number of nodes displayed (50-500)

## Troubleshooting

**"Neo4j not initialized" error:**
- Verify credentials in `.env` file
- Check that your AuraDB instance is running (check Neo4j console)
- Test connection: `python -c "from src.neo4j_graph import Neo4jGraphDB; db = Neo4jGraphDB(); print('Connected!'); db.close()"`

**Graph is empty:**
- Make sure you've run `load_graph_data.py`
- Check that `emails.json` exists and has data
- Verify Neo4j connection

**Connection timeout or SSL errors:**
- Verify URI uses `neo4j+s://` (not `bolt://`) for AuraDB
- Check that your AuraDB instance is active in the console
- Verify username and password are correct
- Check internet connection (AuraDB requires internet access)

**"Invalid authentication" error:**
- Double-check your password (it's case-sensitive)
- Make sure you copied the password correctly from Neo4j console
- If you lost the password, you'll need to reset it in the Neo4j console

## Graph Data Structure

- **Nodes**: Person nodes with email addresses
- **Edges**: COMMUNICATED_WITH relationships with:
  - `count`: Number of communications
  - `subjects`: List of email subjects
  - `first_date`: First communication date
  - `last_date`: Most recent communication date
