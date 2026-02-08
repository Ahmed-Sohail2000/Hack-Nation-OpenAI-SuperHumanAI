# AI Chief of Staff for Organizational Intelligence

A superhuman AI Chief of Staff system that analyzes organizational communications (emails) to provide insights, answer questions, and understand organizational dynamics.

## Features

- **Email Analysis**: Parse and analyze email communications from CSV files
- **Organizational Intelligence**: Understand communication patterns, relationships, and networks
- **AI-Powered Queries**: Ask natural language questions about your organization
- **Graph Visualization**: Interactive Neo4j-powered network graph showing communication relationships
- **Web Interface**: Beautiful, modern web dashboard with tabs for queries, graph, and insights
- **REST API**: Programmatic access to all features

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── data_loader.py              # Load and query email data
│   ├── organizational_intelligence.py  # Analyze organizational patterns
│   ├── ai_chief_of_staff.py        # Main AI interface
│   ├── neo4j_graph.py              # Neo4j graph database integration
│   └── api.py                       # REST API server
├── static/
│   └── index.html                   # Web interface with graph visualization
├── process_emails.py                # Convert CSV emails to JSON
├── load_graph_data.py               # Load emails into Neo4j graph
├── app.py                           # CLI interface
├── run_api.py                       # Run API server
├── requirements.txt                 # Python dependencies
└── .env                            # Configuration file
```

## Setup

### 1. Install Dependencies

```bash
# Activate virtual environment (if using one)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install packages
pip install -r requirements.txt
```

### 2. Set Up Neo4j AuraDB (for Graph Visualization)

**Neo4j AuraDB Cloud Setup:**
1. Sign up for a free account at https://neo4j.com/cloud/aura/
2. Create a free database instance
3. Copy your connection details from the Neo4j console:
   - Connection URI (format: `neo4j+s://xxxxx.databases.neo4j.io`)
   - Username (usually `neo4j`)
   - Password (save this immediately - you can't view it again!)

### 3. Configure Environment

Edit `.env` file and add your configuration:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
PORT=8000
CSV_FILE_PATH=emails.csv
JSON_FILE_PATH=emails.json

# Neo4j AuraDB Configuration
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_aura_password
```

### 4. Process Email Data

If you haven't already, convert your CSV emails to JSON:

```bash
python process_emails.py
```

This will create `emails.json` from `emails.csv`.

### 5. Load Data into Neo4j (for Graph Visualization)

Load your email data into Neo4j:

```bash
python load_graph_data.py
```

This will create nodes (people) and edges (communications) in Neo4j for visualization.

## Usage

### Web Interface (Recommended)

1. **Load data into Neo4j** (first time only):
   ```bash
   python load_graph_data.py
   ```

2. **Start the web server**:
   ```bash
   python run_api.py
   ```

3. **Open your browser**:
   - Go to: **http://localhost:8000**
   - You'll see the AI Chief of Staff dashboard with three tabs:
     - **Query AI**: Ask natural language questions
     - **Communication Graph**: Interactive network visualization
     - **Insights**: Organizational statistics

### CLI Interface

Run the interactive command-line interface:

```bash
python app.py
```

Then ask questions like:
- "Who are the top communicators?"
- "What are the main topics discussed?"
- "Analyze communication patterns for john@example.com"
- Type `insights` for organizational summary
- Type `exit` to quit

### REST API

The API provides several endpoints:

- `GET /api/health` - Health check
- `POST /api/query` - Query the AI Chief of Staff
  ```json
  {
    "query": "Who are the top communicators?",
    "include_emails": true
  }
  ```
- `GET /api/insights` - Get organizational insights
- `POST /api/analyze-person` - Analyze a person's communication patterns
  ```json
  {
    "email": "person@example.com"
  }
  ```
- `GET /api/people` - Get list of all people
- `GET /api/graph` - Get graph data for visualization
  - Query params: `limit` (default: 100)
- `GET /api/graph/person/<email>` - Get communication network for a person
  - Query params: `depth` (default: 2)
- `GET /api/graph/top-relationships` - Get top communication relationships
  - Query params: `limit` (default: 20)

## Example Queries

- "What are the main communication patterns in the organization?"
- "Who communicates most frequently with whom?"
- "What topics are discussed most often?"
- "Analyze the role of [email] in the organization"
- "What are the busiest communication periods?"
- "Who are the key influencers in the organization?"

## Requirements

- Python 3.8+
- OpenAI API key
- Neo4j database (for graph visualization - optional but recommended)
- Email data in CSV format (with 'file' and 'message' columns)

## License

See LICENSE file for details.
