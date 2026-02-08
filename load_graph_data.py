"""
Load email data into Neo4j graph database.
"""
import os
import json
from dotenv import load_dotenv
from src.neo4j_graph import Neo4jGraphDB
from src.data_loader import EmailDataLoader

load_dotenv()


def main():
    """Load emails into Neo4j graph database."""
    print("=" * 60)
    print("Loading Email Data into Neo4j Graph Database")
    print("=" * 60)
    print()
    
    # Initialize data loader
    json_file = os.getenv("JSON_FILE_PATH", "emails.json")
    data_loader = EmailDataLoader(json_file)
    
    print(f"Loading emails from {json_file}...")
    emails = data_loader.load()
    print(f"Loaded {len(emails)} emails")
    print()
    
    # Initialize Neo4j
    try:
        neo4j = Neo4jGraphDB()
        print("Connected to Neo4j")
        print()
        
        # Ask user if they want to clear existing data
        response = input("Clear existing graph data? (y/n): ").strip().lower()
        if response == 'y':
            print("Clearing existing data...")
            neo4j.clear_database()
            print("Database cleared")
            print()
        
        # Load emails into Neo4j
        neo4j.load_emails(emails)
        print()
        print("=" * 60)
        print("Successfully loaded emails into Neo4j!")
        print("=" * 60)
        
        # Show some stats
        graph_data = neo4j.get_graph_data(limit=10)
        print(f"\nGraph Statistics:")
        print(f"  Nodes (People): {len(graph_data['nodes'])}")
        print(f"  Edges (Communications): {len(graph_data['edges'])}")
        
        neo4j.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n📋 Troubleshooting Steps:")
        print("1. Check your .env file has Neo4j AuraDB credentials:")
        print("   NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io")
        print("   NEO4J_USER=neo4j")
        print("   NEO4J_PASSWORD=your_password")
        print("\n2. Verify your Neo4j AuraDB instance is running:")
        print("   - Go to https://console.neo4j.io/")
        print("   - Check that your database shows as 'Running'")
        print("\n3. Test connection manually:")
        print("   python -c \"from src.neo4j_graph import Neo4jGraphDB; db = Neo4jGraphDB(); print('Connected!'); db.close()\"")
        print("\n4. Make sure emails.json exists:")
        print("   - Run: python process_emails.py (if not done already)")


if __name__ == "__main__":
    main()
