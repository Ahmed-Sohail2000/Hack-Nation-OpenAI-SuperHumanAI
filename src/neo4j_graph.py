"""
Neo4j graph database integration for communication network visualization.
"""
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()


class Neo4jGraphDB:
    """Neo4j graph database for storing and querying communication networks."""
    
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, 
                 password: Optional[str] = None):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j database URI (default: from NEO4J_URI env var)
            user: Neo4j username (default: from NEO4J_USER env var)
            password: Neo4j password (default: from NEO4J_PASSWORD env var)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "neo4j+s://xxxxx.databases.neo4j.io")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
    
    def close(self):
        """Close the database connection."""
        self.driver.close()
    
    def clear_database(self):
        """Clear all nodes and relationships from the database."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def create_person(self, email: str, name: Optional[str] = None):
        """
        Create or update a person node.
        
        Args:
            email: Email address (unique identifier)
            name: Optional name for the person
        """
        with self.driver.session() as session:
            session.run(
                "MERGE (p:Person {email: $email}) "
                "SET p.name = COALESCE($name, p.name, $email) "
                "SET p.updated = datetime()",
                email=email,
                name=name
            )
    
    def create_communication(self, sender: str, receiver: str, 
                            subject: Optional[str] = None,
                            timestamp: Optional[str] = None,
                            email_id: Optional[str] = None):
        """
        Create a communication relationship between two people.
        
        Args:
            sender: Sender's email address
            receiver: Receiver's email address
            subject: Email subject
            timestamp: Email timestamp
            email_id: Unique email identifier
        """
        with self.driver.session() as session:
            # Create sender if doesn't exist
            session.run(
                "MERGE (s:Person {email: $sender})",
                sender=sender
            )
            
            # Create receiver if doesn't exist
            session.run(
                "MERGE (r:Person {email: $receiver})",
                receiver=receiver
            )
            
            # Create or update communication relationship
            session.run(
                "MATCH (s:Person {email: $sender}), (r:Person {email: $receiver}) "
                "MERGE (s)-[c:COMMUNICATED_WITH]->(r) "
                "ON CREATE SET c.count = 1, c.subjects = CASE WHEN $subject = '' THEN [] ELSE [$subject] END, c.first_date = $timestamp, c.last_date = $timestamp "
                "ON MATCH SET c.count = c.count + 1, "
                "  c.subjects = CASE WHEN $subject = '' OR $subject IN c.subjects THEN c.subjects ELSE c.subjects + [$subject] END, "
                "  c.last_date = $timestamp",
                sender=sender,
                receiver=receiver,
                subject=subject or "",
                timestamp=timestamp or ""
            )
    
    def load_emails(self, emails: List[Dict[str, Any]]):
        """
        Load email data into Neo4j graph.
        
        Args:
            emails: List of email dictionaries
        """
        print(f"Loading {len(emails)} emails into Neo4j...")
        
        for i, email in enumerate(emails):
            sender = email.get('sender', '').strip()
            receivers = email.get('receiver', [])
            subject = email.get('subject', '')
            timestamp = email.get('timestamp', '')
            
            if not sender:
                continue
            
            # Create sender node
            self.create_person(sender)
            
            # Create communication relationships
            for receiver in receivers:
                if receiver and receiver.strip():
                    self.create_communication(
                        sender=sender,
                        receiver=receiver.strip(),
                        subject=subject,
                        timestamp=timestamp,
                        email_id=f"email_{i}"
                    )
            
            if (i + 1) % 1000 == 0:
                print(f"Processed {i + 1} emails...")
        
        print("Finished loading emails into Neo4j")
    
    def get_graph_data(self, limit: int = 100) -> Dict[str, Any]:
        """
        Get graph data for visualization.
        
        Args:
            limit: Maximum number of nodes to return
            
        Returns:
            Dictionary with nodes and edges for visualization
        """
        with self.driver.session() as session:
            # Get nodes (people) with their communication counts
            nodes_query = """
            MATCH (p:Person)
            OPTIONAL MATCH (p)-[c:COMMUNICATED_WITH]->()
            WITH p, count(c) as out_count
            OPTIONAL MATCH ()-[c2:COMMUNICATED_WITH]->(p)
            WITH p, out_count, count(c2) as in_count
            WITH p, out_count + in_count as total_communications
            ORDER BY total_communications DESC
            LIMIT $limit
            RETURN p.email as id, p.name as label, total_communications as value
            """
            
            nodes_result = session.run(nodes_query, limit=limit)
            nodes = [{"id": record["id"], "label": record["label"] or record["id"], 
                     "value": record["value"]} for record in nodes_result]
            
            # Get edges (communications) between the selected nodes
            node_ids = [node["id"] for node in nodes]
            if not node_ids:
                return {"nodes": [], "edges": []}
            
            edges_query = """
            MATCH (s:Person)-[c:COMMUNICATED_WITH]->(r:Person)
            WHERE s.email IN $node_ids AND r.email IN $node_ids
            RETURN s.email as from, r.email as to, c.count as value, 
                   c.subjects as subjects, c.last_date as last_date
            ORDER BY c.count DESC
            """
            
            edges_result = session.run(edges_query, node_ids=node_ids)
            edges = [{"from": record["from"], "to": record["to"], 
                     "value": record["value"], 
                     "subjects": record["subjects"][:3] if record["subjects"] else [],
                     "last_date": record["last_date"]} for record in edges_result]
            
            return {"nodes": nodes, "edges": edges}
    
    def get_person_network(self, email: str, depth: int = 2) -> Dict[str, Any]:
        """
        Get communication network for a specific person.
        
        Args:
            email: Person's email address
            depth: Network depth to explore
            
        Returns:
            Dictionary with nodes and edges
        """
        with self.driver.session() as session:
            # Get person and their network
            query = f"""
            MATCH path = (p:Person {{email: $email}})-[*1..{depth}]-(connected:Person)
            WITH DISTINCT connected, p
            RETURN connected.email as id, connected.name as label
            UNION
            MATCH (p:Person {{email: $email}})
            RETURN p.email as id, p.name as label
            """
            
            nodes_result = session.run(query, email=email)
            nodes = [{"id": record["id"], "label": record["label"] or record["id"]} 
                    for record in nodes_result]
            
            node_ids = [node["id"] for node in nodes]
            
            edges_query = """
            MATCH (s:Person)-[c:COMMUNICATED_WITH]->(r:Person)
            WHERE s.email IN $node_ids AND r.email IN $node_ids
            RETURN s.email as from, r.email as to, c.count as value
            """
            
            edges_result = session.run(edges_query, node_ids=node_ids)
            edges = [{"from": record["from"], "to": record["to"], 
                     "value": record["value"]} for record in edges_result]
            
            return {"nodes": nodes, "edges": edges}
    
    def get_top_relationships(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get top communication relationships.
        
        Args:
            limit: Number of top relationships to return
            
        Returns:
            List of relationship dictionaries
        """
        with self.driver.session() as session:
            query = """
            MATCH (s:Person)-[c:COMMUNICATED_WITH]->(r:Person)
            RETURN s.email as sender, r.email as receiver, c.count as count,
                   c.subjects as subjects, c.last_date as last_date
            ORDER BY c.count DESC
            LIMIT $limit
            """
            
            result = session.run(query, limit=limit)
            return [{"sender": record["sender"], "receiver": record["receiver"],
                    "count": record["count"], "subjects": record["subjects"],
                    "last_date": record["last_date"]} for record in result]
