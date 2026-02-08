# How to Load Graph Data into Neo4j

## Quick Steps

### Step 1: Verify Your Setup

Make sure you have:
- ✅ Neo4j AuraDB credentials in `.env` file
- ✅ `emails.json` file exists (run `python process_emails.py` if needed)
- ✅ Neo4j AuraDB instance is running (check at https://console.neo4j.io/)

### Step 2: Run the Data Loader

Open a **new terminal/command prompt** (keep your API server running in another terminal) and run:

```bash
python load_graph_data.py
```

### Step 3: Follow the Prompts

The script will:
1. Load emails from `emails.json`
2. Ask if you want to clear existing data (type `y` or `n`)
3. Load all emails into Neo4j (this may take several minutes)
4. Show statistics when done

### Step 4: Refresh the Graph

Once loading is complete:
1. Go back to your browser
2. Click the "Communication Graph" tab
3. Click "Load Graph" button
4. You should now see the visualization!

## Expected Output

When successful, you'll see:
```
============================================================
Loading Email Data into Neo4j Graph Database
============================================================

Loading emails from emails.json...
Loaded 50000 emails

Connected to Neo4j

Clear existing graph data? (y/n): n

Loading 50000 emails into Neo4j...
Processed 1000 emails...
Processed 2000 emails...
...
Finished loading emails into Neo4j

============================================================
Successfully loaded emails into Neo4j!
============================================================

Graph Statistics:
  Nodes (People): 150
  Edges (Communications): 5000
```

## Troubleshooting

### "Error: Could not connect to Neo4j"
- Check your `.env` file has correct credentials
- Verify your AuraDB instance is running
- Make sure URI uses `neo4j+s://` (not `bolt://`)

### "emails.json not found"
- Run: `python process_emails.py` first
- Make sure the file is in the project root directory

### "No data loaded"
- Check that `emails.json` has actual email data
- Verify emails have sender and receiver fields
- Check the console for any error messages

### Loading is very slow
- This is normal for large datasets
- The script shows progress every 1000 emails
- Be patient - it will complete!

## After Loading

Once data is loaded:
- ✅ Graph will show in the web interface
- ✅ You can query communication patterns
- ✅ Network visualization will work
- ✅ Person analysis will be available

**Note:** You only need to load data once (unless you have new emails to add).
