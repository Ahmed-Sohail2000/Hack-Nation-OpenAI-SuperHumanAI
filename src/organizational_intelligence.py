"""
Organizational Intelligence module for analyzing email communications.
"""
from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from src.data_loader import EmailDataLoader


class OrganizationalIntelligence:
    """Analyze organizational patterns from email data."""
    
    def __init__(self, data_loader: EmailDataLoader):
        """
        Initialize organizational intelligence analyzer.
        
        Args:
            data_loader: EmailDataLoader instance
        """
        self.data_loader = data_loader
        self.data_loader.load()
    
    def get_communication_network(self) -> Dict[str, Dict[str, int]]:
        """
        Build communication network graph.
        
        Returns:
            Dictionary mapping sender -> {receiver: count}
        """
        network = defaultdict(lambda: defaultdict(int))
        
        for email in self.data_loader.emails:
            sender = email.get('sender', '')
            receivers = email.get('receiver', [])
            
            if sender:
                for receiver in receivers:
                    if receiver:
                        network[sender][receiver] += 1
        
        return dict(network)
    
    def get_top_communicators(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Get top communicators by email count.
        
        Args:
            top_n: Number of top communicators to return
            
        Returns:
            List of (email, count) tuples
        """
        sender_counts = Counter()
        receiver_counts = Counter()
        
        for email in self.data_loader.emails:
            sender = email.get('sender', '')
            receivers = email.get('receiver', [])
            
            if sender:
                sender_counts[sender] += 1
            
            for receiver in receivers:
                if receiver:
                    receiver_counts[receiver] += 1
        
        # Combine sender and receiver counts
        all_counts = sender_counts + receiver_counts
        
        return all_counts.most_common(top_n)
    
    def get_communication_patterns(self, person: str) -> Dict[str, Any]:
        """
        Get communication patterns for a specific person.
        
        Args:
            person: Email address of the person
            
        Returns:
            Dictionary with communication statistics
        """
        sent = self.data_loader.get_emails_by_sender(person)
        received = self.data_loader.get_emails_by_receiver(person)
        
        # Get most frequent correspondents
        correspondents = Counter()
        for email in sent:
            for receiver in email.get('receiver', []):
                if receiver:
                    correspondents[receiver] += 1
        
        for email in received:
            sender = email.get('sender', '')
            if sender:
                correspondents[sender] += 1
        
        # Get time-based patterns
        sent_times = [e.get('parsed_timestamp') for e in sent if e.get('parsed_timestamp')]
        received_times = [e.get('parsed_timestamp') for e in received if e.get('parsed_timestamp')]
        
        return {
            'sent_count': len(sent),
            'received_count': len(received),
            'total_communications': len(sent) + len(received),
            'top_correspondents': correspondents.most_common(10),
            'sent_times': sent_times,
            'received_times': received_times
        }
    
    def get_topic_clusters(self, min_emails: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify topic clusters based on subject lines.
        
        Args:
            min_emails: Minimum number of emails per cluster
            
        Returns:
            Dictionary mapping topic keywords to email lists
        """
        subject_keywords = defaultdict(list)
        
        for email in self.data_loader.emails:
            subject = email.get('subject', '').lower()
            if not subject:
                continue
            
            # Extract common keywords (simple approach)
            words = subject.split()
            for word in words:
                if len(word) > 4:  # Filter short words
                    subject_keywords[word].append(email)
        
        # Filter by minimum count
        clusters = {
            keyword: emails 
            for keyword, emails in subject_keywords.items() 
            if len(emails) >= min_emails
        }
        
        return clusters
    
    def get_organizational_insights(self) -> Dict[str, Any]:
        """
        Generate high-level organizational insights.
        
        Returns:
            Dictionary with various organizational metrics
        """
        emails = self.data_loader.emails
        
        # Basic statistics
        total_emails = len(emails)
        unique_senders = len(self.data_loader.get_all_senders())
        unique_receivers = len(self.data_loader.get_all_receivers())
        
        # Communication volume over time
        date_range = self.data_loader.get_date_range()
        
        # Average response time (if we can determine threads)
        # This is a simplified version
        
        return {
            'total_emails': total_emails,
            'unique_senders': unique_senders,
            'unique_receivers': unique_receivers,
            'date_range': {
                'earliest': date_range[0].isoformat() if date_range[0] else None,
                'latest': date_range[1].isoformat() if date_range[1] else None
            },
            'top_communicators': self.get_top_communicators(10),
            'communication_network_size': len(self.get_communication_network())
        }
