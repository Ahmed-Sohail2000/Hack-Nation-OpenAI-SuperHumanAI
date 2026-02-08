"""
Agentic Reasoning Layer for AI Chief of Staff.
Implements Memory, Critic, and Coordinator agents.
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from src.data_loader import EmailDataLoader
from src.organizational_intelligence import OrganizationalIntelligence


class MemoryAgent:
    """Agent responsible for updating and versioning organizational knowledge."""
    
    def __init__(self, data_loader: EmailDataLoader):
        self.data_loader = data_loader
        self.memory_file = "knowledge_memory.json"
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load existing memory from file."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "version": 1,
            "last_updated": None,
            "knowledge_base": {},
            "communication_patterns": {},
            "topics": {},
            "relationships": {}
        }
    
    def _save_memory(self):
        """Save memory to file."""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def update_knowledge(self) -> Dict[str, Any]:
        """Update knowledge base with current email data."""
        emails = self.data_loader.load()
        org_intel = OrganizationalIntelligence(self.data_loader)
        
        # Update communication patterns
        network = org_intel.get_communication_network()
        top_communicators = org_intel.get_top_communicators(20)
        topics = org_intel.get_topic_clusters()
        
        # Version the knowledge
        self.memory["version"] += 1
        self.memory["last_updated"] = datetime.now().isoformat()
        
        # Store knowledge
        self.memory["knowledge_base"][f"v{self.memory['version']}"] = {
            "timestamp": datetime.now().isoformat(),
            "total_emails": len(emails),
            "network_size": len(network),
            "top_communicators": [(email, count) for email, count in top_communicators],
            "topic_count": len(topics)
        }
        
        self.memory["communication_patterns"] = {
            "network": {k: dict(v) for k, v in network.items()},
            "top_communicators": [(email, count) for email, count in top_communicators]
        }
        
        self.memory["topics"] = {
            topic: len(emails) for topic, emails in topics.items()
        }
        
        self._save_memory()
        
        return {
            "version": self.memory["version"],
            "updated": self.memory["last_updated"],
            "summary": f"Updated to version {self.memory['version']}"
        }
    
    def get_knowledge_version(self) -> int:
        """Get current knowledge version."""
        return self.memory.get("version", 1)
    
    def get_what_changed(self, days: int = 1) -> Dict[str, Any]:
        """Generate 'What Changed Today' summary."""
        current_version = self.memory.get("version", 1)
        if current_version < 2:
            return {"message": "Insufficient history. Need at least 2 versions to detect changes."}
        
        # Safely access current and previous versions
        current_key = f"v{current_version}"
        previous_key = f"v{current_version - 1}"
        
        if current_key not in self.memory.get("knowledge_base", {}):
            return {"message": "Current version not found in knowledge base."}
        
        current = self.memory["knowledge_base"][current_key]
        previous = self.memory["knowledge_base"].get(previous_key, {})
        
        changes = {
            "version": self.memory["version"],
            "timestamp": current.get("timestamp"),
            "changes": []
        }
        
        # Detect changes
        if current.get("total_emails", 0) != previous.get("total_emails", 0):
            changes["changes"].append({
                "type": "email_count",
                "previous": previous.get("total_emails", 0),
                "current": current.get("total_emails", 0),
                "delta": current.get("total_emails", 0) - previous.get("total_emails", 0)
            })
        
        # Compare top communicators
        prev_comm = {email: count for email, count in previous.get("top_communicators", [])}
        curr_comm = {email: count for email, count in current.get("top_communicators", [])}
        
        for email, count in curr_comm.items():
            prev_count = prev_comm.get(email, 0)
            if count != prev_count:
                changes["changes"].append({
                    "type": "communicator_activity",
                    "person": email,
                    "previous": prev_count,
                    "current": count,
                    "delta": count - prev_count
                })
        
        return changes


class CriticAgent:
    """Agent responsible for detecting conflicts and duplicated topics."""
    
    def __init__(self, data_loader: EmailDataLoader):
        self.data_loader = data_loader
        self.org_intel = OrganizationalIntelligence(data_loader)
    
    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """Detect conflicting decisions or duplicated topics."""
        conflicts = []
        emails = self.data_loader.load()
        
        # Group emails by subject similarity
        subject_groups = defaultdict(list)
        for email in emails:
            subject = email.get('subject', '').lower().strip()
            if subject:
                # Simple grouping by key words
                key_words = [w for w in subject.split() if len(w) > 4]
                if key_words:
                    group_key = key_words[0]  # Use first significant word
                    subject_groups[group_key].append(email)
        
        # Detect duplicated topics
        for topic, topic_emails in subject_groups.items():
            if len(topic_emails) > 10:  # Threshold for duplication
                senders = [e.get('sender') for e in topic_emails if e.get('sender')]
                unique_senders = len(set(senders))
                
                if unique_senders > 5:  # Multiple people discussing same topic
                    conflicts.append({
                        "type": "duplicated_topic",
                        "topic": topic,
                        "email_count": len(topic_emails),
                        "participants": unique_senders,
                        "severity": "medium" if len(topic_emails) < 20 else "high"
                    })
        
        # Detect conflicting communications (same people, different topics)
        network = self.org_intel.get_communication_network()
        for sender, receivers in network.items():
            if len(receivers) > 10:  # High communication volume
                # Check for topic diversity
                sender_emails = self.data_loader.get_emails_by_sender(sender)
                subjects = [e.get('subject', '') for e in sender_emails[:20] if e.get('subject', '').strip()]
                unique_subjects = len(set([s.lower() for s in subjects if s]))
                
                # Only check topic diversity if we have subjects to analyze
                if len(subjects) > 0 and unique_subjects < len(subjects) * 0.3:  # Low topic diversity
                    conflicts.append({
                        "type": "topic_concentration",
                        "person": sender,
                        "communication_count": sum(receivers.values()),
                        "unique_topics": unique_subjects,
                        "severity": "low"
                    })
        
        return conflicts
    
    def analyze_duplications(self) -> Dict[str, Any]:
        """Analyze topic duplications."""
        topics = self.org_intel.get_topic_clusters(min_emails=3)
        
        return {
            "total_topics": len(topics),
            "duplicated_topics": {k: len(v) for k, v in topics.items() if len(v) > 5},
            "summary": f"Found {len(topics)} topic clusters, {len([v for v in topics.values() if len(v) > 5])} with significant duplication"
        }


class CoordinatorAgent:
    """Agent responsible for determining relevant stakeholders."""
    
    def __init__(self, data_loader: EmailDataLoader):
        self.data_loader = data_loader
        self.org_intel = OrganizationalIntelligence(data_loader)
    
    def get_stakeholders(self, topic: Optional[str] = None, 
                        person: Optional[str] = None) -> Dict[str, Any]:
        """Determine relevant stakeholders for a topic or person."""
        if topic:
            # Find stakeholders for a specific topic
            relevant_emails = self.data_loader.get_emails_by_keyword(topic)
            stakeholders = set()
            
            for email in relevant_emails:
                if email.get('sender'):
                    stakeholders.add(email['sender'])
                stakeholders.update(email.get('receiver', []))
            
            # Rank by involvement
            involvement = defaultdict(int)
            for email in relevant_emails:
                if email.get('sender'):
                    involvement[email['sender']] += 1
                for receiver in email.get('receiver', []):
                    involvement[receiver] += 1
            
            ranked_stakeholders = sorted(
                involvement.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return {
                "topic": topic,
                "stakeholders": [{"email": email, "involvement": count} 
                               for email, count in ranked_stakeholders[:10]],
                "total_emails": len(relevant_emails)
            }
        
        elif person:
            # Find stakeholders connected to a person
            patterns = self.org_intel.get_communication_patterns(person)
            top_correspondents = patterns.get('top_correspondents', [])
            
            return {
                "person": person,
                "stakeholders": [{"email": email, "communications": count} 
                               for email, count in top_correspondents[:10]],
                "total_communications": patterns.get('total_communications', 0)
            }
        
        else:
            # Get all key stakeholders
            top_communicators = self.org_intel.get_top_communicators(20)
            
            return {
                "type": "all_stakeholders",
                "stakeholders": [{"email": email, "communications": count} 
                               for email, count in top_communicators],
                "total": len(top_communicators)
            }
    
    def get_stakeholder_relevance(self, topic: str) -> Dict[str, Any]:
        """Get stakeholder relevance for a specific topic."""
        # Validate topic parameter
        if not topic or not isinstance(topic, str) or not topic.strip():
            return {
                "error": "Topic must be a non-empty string",
                "topic": topic,
                "relevance_breakdown": {
                    "high": [],
                    "medium": [],
                    "low": []
                },
                "summary": {
                    "high_count": 0,
                    "medium_count": 0,
                    "low_count": 0,
                    "total_stakeholders": 0
                }
            }
        
        stakeholders_data = self.get_stakeholders(topic=topic)
        
        # Categorize stakeholders by relevance level
        # Handle case where stakeholders might not have "involvement" field
        high_relevance = [s for s in stakeholders_data["stakeholders"] 
                         if s.get("involvement", 0) >= 5]
        medium_relevance = [s for s in stakeholders_data["stakeholders"] 
                          if 2 <= s.get("involvement", 0) < 5]
        low_relevance = [s for s in stakeholders_data["stakeholders"] 
                        if s.get("involvement", 0) < 2]
        
        return {
            "topic": topic,
            "relevance_breakdown": {
                "high": high_relevance,
                "medium": medium_relevance,
                "low": low_relevance
            },
            "summary": {
                "high_count": len(high_relevance),
                "medium_count": len(medium_relevance),
                "low_count": len(low_relevance),
                "total_stakeholders": len(stakeholders_data["stakeholders"])
            }
        }


def log_agent_output(agent_name: str, output: Dict[str, Any], 
                    log_file: str = "agent_logs.json"):
    """Log agent outputs as structured JSON."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "output": output
    }
    
    # Load existing logs
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            pass
    
    # Append new log
    logs.append(log_entry)
    
    # Save (keep last 1000 entries)
    logs = logs[-1000:]
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)
    
    return log_entry
