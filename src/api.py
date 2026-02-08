"""
REST API for AI Chief of Staff.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

from src.ai_chief_of_staff import AICChiefOfStaff
from src.neo4j_graph import Neo4jGraphDB
from src.agents import MemoryAgent, CriticAgent, CoordinatorAgent, log_agent_output

load_dotenv()

# Get the base directory (project root)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, static_folder=static_dir, static_url_path='/static')
CORS(app)  # Enable CORS for frontend

# Initialize AI Chief of Staff
json_file = os.getenv("JSON_FILE_PATH", "emails.json")
chief_of_staff = None

try:
    chief_of_staff = AICChiefOfStaff(json_file_path=json_file)
except Exception as e:
    print(f"Warning: Could not initialize AI Chief of Staff: {e}")

# Initialize Neo4j
neo4j_db = None
try:
    neo4j_db = Neo4jGraphDB()
    print("Neo4j connection established")
except Exception as e:
    print(f"Warning: Could not connect to Neo4j: {e}")
    print("Graph features will be unavailable")

# Initialize Agents
memory_agent = None
critic_agent = None
coordinator_agent = None

try:
    if chief_of_staff:
        memory_agent = MemoryAgent(chief_of_staff.data_loader)
        critic_agent = CriticAgent(chief_of_staff.data_loader)
        coordinator_agent = CoordinatorAgent(chief_of_staff.data_loader)
        print("Agentic reasoning layer initialized")
except Exception as e:
    print(f"Warning: Could not initialize agents: {e}")


@app.route('/', methods=['GET'])
def index():
    """Serve the main page."""
    from flask import send_from_directory
    return send_from_directory(static_dir, 'index.html')


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "initialized": chief_of_staff is not None})


@app.route('/api/query', methods=['POST'])
def query():
    """Query the AI Chief of Staff."""
    if not chief_of_staff:
        return jsonify({"error": "AI Chief of Staff not initialized"}), 500
    
    data = request.get_json()
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({"error": "Query is required"}), 400
    
    include_emails = data.get('include_emails', True)
    
    try:
        result = chief_of_staff.query(user_query, include_emails=include_emails)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/insights', methods=['GET'])
def insights():
    """Get organizational insights."""
    if not chief_of_staff:
        return jsonify({"error": "AI Chief of Staff not initialized"}), 500
    
    try:
        insights_data = chief_of_staff.get_insights()
        return jsonify(insights_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/analyze-person', methods=['POST'])
def analyze_person():
    """Analyze a specific person's communication patterns."""
    if not chief_of_staff:
        return jsonify({"error": "AI Chief of Staff not initialized"}), 500
    
    data = request.get_json()
    email_address = data.get('email', '')
    
    if not email_address:
        return jsonify({"error": "Email address is required"}), 400
    
    try:
        result = chief_of_staff.analyze_person(email_address)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/people', methods=['GET'])
def get_people():
    """Get list of all people in the organization."""
    if not chief_of_staff:
        return jsonify({"error": "AI Chief of Staff not initialized"}), 500
    
    try:
        senders = chief_of_staff.data_loader.get_all_senders()
        receivers = chief_of_staff.data_loader.get_all_receivers()
        all_people = sorted(list(set(senders + receivers)))
        return jsonify({"people": all_people, "count": len(all_people)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/graph', methods=['GET'])
def get_graph():
    """Get graph data for visualization."""
    if not neo4j_db:
        return jsonify({
            "error": "Neo4j not initialized. Please check your .env file has correct NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD.",
            "nodes": [],
            "edges": []
        }), 200
    
    try:
        limit = int(request.args.get('limit', 100))
        graph_data = neo4j_db.get_graph_data(limit=limit)
        
        # Check if database is empty
        if not graph_data.get('nodes') or len(graph_data.get('nodes', [])) == 0:
            return jsonify({
                "error": "No data in Neo4j. Please run: python load_graph_data.py to load email data.",
                "nodes": [],
                "edges": []
            }), 200
        
        return jsonify(graph_data)
    except Exception as e:
        return jsonify({
            "error": f"Error loading graph: {str(e)}. Make sure Neo4j AuraDB is running and accessible.",
            "nodes": [],
            "edges": []
        }), 200


@app.route('/api/graph/person/<email>', methods=['GET'])
def get_person_network(email):
    """Get communication network for a specific person."""
    if not neo4j_db:
        return jsonify({"error": "Neo4j not initialized"}), 500
    
    try:
        depth = int(request.args.get('depth', 2))
        graph_data = neo4j_db.get_person_network(email, depth=depth)
        return jsonify(graph_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/graph/top-relationships', methods=['GET'])
def get_top_relationships():
    """Get top communication relationships."""
    if not neo4j_db:
        return jsonify({"error": "Neo4j not initialized"}), 500
    
    try:
        limit = int(request.args.get('limit', 20))
        relationships = neo4j_db.get_top_relationships(limit=limit)
        return jsonify({"relationships": relationships})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Agentic Reasoning Endpoints
@app.route('/api/agents/memory', methods=['POST'])
def run_memory_agent():
    """Run Memory Agent to update knowledge."""
    if not memory_agent:
        return jsonify({"error": "Memory Agent not initialized"}), 500
    
    try:
        result = memory_agent.update_knowledge()
        log_agent_output("MemoryAgent", result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/critic', methods=['POST'])
def run_critic_agent():
    """Run Critic Agent to detect conflicts."""
    if not critic_agent:
        return jsonify({"error": "Critic Agent not initialized"}), 500
    
    try:
        conflicts = critic_agent.detect_conflicts()
        duplications = critic_agent.analyze_duplications()
        result = {
            "conflicts": conflicts,
            "duplications": duplications,
            "summary": f"Found {len(conflicts)} potential conflicts and {duplications.get('total_topics', 0)} topic clusters"
        }
        log_agent_output("CriticAgent", result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/coordinator', methods=['POST'])
def run_coordinator_agent():
    """Run Coordinator Agent to identify stakeholders."""
    if not coordinator_agent:
        return jsonify({"error": "Coordinator Agent not initialized"}), 500
    
    try:
        data = request.get_json() or {}
        topic = data.get('topic')
        person = data.get('person')
        
        if topic:
            result = coordinator_agent.get_stakeholder_relevance(topic)
        elif person:
            result = coordinator_agent.get_stakeholders(person=person)
        else:
            result = coordinator_agent.get_stakeholders()
        
        log_agent_output("CoordinatorAgent", result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/what-changed', methods=['POST'])
def get_what_changed():
    """Get 'What Changed Today' summary."""
    if not memory_agent:
        return jsonify({"error": "Memory Agent not initialized"}), 500
    
    try:
        data = request.get_json() or {}
        days = data.get('days', 1)
        result = memory_agent.get_what_changed(days=days)
        log_agent_output("WhatChanged", result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    app.run(debug=True, host='127.0.0.1', port=port)
