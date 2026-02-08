# Neo4j AuraDB Setup Guide

## Step-by-Step Setup for Neo4j AuraDB (Cloud)

### 1. Create Neo4j AuraDB Account

1. Go to https://neo4j.com/cloud/aura/
2. Click "Start Free" or "Sign Up"
3. Sign up with your email or use Google/GitHub
4. Verify your email if required

### 2. Create a Free Database Instance

1. After logging in, you'll be in the Neo4j Console (https://console.neo4j.io/)
2. Click **"Create Database"** button
3. Select **"Free Instance"** (or "Free Tier")
4. Fill in the form:
   - **Database Name**: Choose a name (e.g., "organizational-intelligence")
   - **Region**: Choose closest to you (e.g., "US East (Ohio)")
   - **Cloud Provider**: AWS (default)
5. Click **"Create Database"**
6. Wait 2-3 minutes for the database to be created

### 3. Get Your Connection Details

Once your database is created:

1. Click on your database name in the list
2. You'll see connection details. Look for:
   - **Connection URI**: Something like `neo4j+s://a1b2c3d4.databases.neo4j.io`
   - **Username**: Usually `neo4j`
   - **Password**: Click **"Show Password"** or **"Copy Password"**
     - ⚠️ **IMPORTANT**: Save this password immediately! You won't be able to see it again.
     - If you lose it, you'll need to reset it in the console

### 4. Configure Your .env File

Edit your `.env` file and add:

```env
# Neo4j AuraDB Configuration
NEO4J_URI=neo4j+s://your-instance-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
```

**Example:**
```env
NEO4J_URI=neo4j+s://a1b2c3d4e5f6.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=MySecurePassword123!xyz
```

### 5. Test Your Connection

Test that your connection works:

```bash
python -c "from src.neo4j_graph import Neo4jGraphDB; db = Neo4jGraphDB(); print('✓ Connected to Neo4j AuraDB!'); db.close()"
```

If you see "✓ Connected to Neo4j AuraDB!", you're all set!

### 6. Load Your Data

Once connected, load your email data:

```bash
python load_graph_data.py
```

This will populate your Neo4j database with communication relationships.

## Important Notes

### URI Format
- **AuraDB uses**: `neo4j+s://` (secure connection)
- **NOT**: `bolt://` (that's for local Neo4j Desktop)
- The `+s` means it uses SSL/TLS encryption

### Free Tier Limits
- **50,000 nodes** (people)
- **175,000 relationships** (communications)
- **0.5 GB storage**
- Perfect for most organizational intelligence use cases!

### Security
- Your password is shown only once when you create the database
- If you lose it, go to your database → Settings → Reset Password
- The connection is encrypted (that's what the `+s` means)

### Accessing Your Database

You can also access your database through:
- **Neo4j Browser**: Click "Open" in the console to open Neo4j Browser
- **Neo4j Bloom**: Available in paid tiers
- **Your Application**: Using the connection URI in `.env`

## Troubleshooting

### "Invalid authentication" error
- Double-check your password (it's case-sensitive)
- Make sure you copied it correctly
- Try resetting the password in the Neo4j console

### "Connection timeout" error
- Check your internet connection
- Verify the URI is correct (should start with `neo4j+s://`)
- Make sure your database is running (check the console)

### "SSL/TLS" errors
- Make sure you're using `neo4j+s://` not `bolt://`
- The `+s` is required for AuraDB secure connections

### Can't find password
- Go to your database in the console
- Click "Connection Details" or "Settings"
- Look for "Reset Password" if you need to create a new one

## Next Steps

Once your database is set up:
1. ✅ Test connection (step 5 above)
2. ✅ Load data: `python load_graph_data.py`
3. ✅ Start API: `python run_api.py`
4. ✅ Open browser: `http://localhost:8000`
5. ✅ View graph in the "Communication Graph" tab

Enjoy your organizational intelligence platform! 🚀
