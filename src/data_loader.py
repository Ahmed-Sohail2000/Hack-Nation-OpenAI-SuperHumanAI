"""
Data loader for email data and organizational intelligence.
"""
import json
import os
from typing import List, Dict, Any
from datetime import datetime
from email.utils import parsedate_to_datetime


class EmailDataLoader:
    """Load and manage email data from JSON files."""
    
    def __init__(self, json_file_path: str = "emails.json"):
        """
        Initialize the email data loader.
        
        Args:
            json_file_path: Path to the JSON file containing emails
        """
        self.json_file_path = json_file_path
        self.emails: List[Dict[str, Any]] = []
        self.loaded = False
    
    def load(self) -> List[Dict[str, Any]]:
        """
        Load emails from JSON file.
        
        Returns:
            List of email dictionaries
        """
        if self.loaded:
            return self.emails
        
        if not os.path.exists(self.json_file_path):
            raise FileNotFoundError(f"Email data file not found: {self.json_file_path}")
        
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            self.emails = json.load(f)
        
        # Parse timestamps to datetime objects for easier querying
        for email in self.emails:
            if email.get('timestamp'):
                try:
                    email['parsed_timestamp'] = parsedate_to_datetime(email['timestamp'])
                except (ValueError, TypeError):
                    email['parsed_timestamp'] = None
        
        self.loaded = True
        return self.emails
    
    def get_emails_by_sender(self, sender: str) -> List[Dict[str, Any]]:
        """Get all emails from a specific sender."""
        if not self.loaded:
            self.load()
        return [e for e in self.emails if e.get('sender', '').lower() == sender.lower()]
    
    def get_emails_by_receiver(self, receiver: str) -> List[Dict[str, Any]]:
        """Get all emails to a specific receiver."""
        if not self.loaded:
            self.load()
        return [e for e in self.emails if receiver.lower() in [r.lower() for r in e.get('receiver', [])]]
    
    def get_emails_by_keyword(self, keyword: str, search_fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search emails by keyword in specified fields.
        
        Args:
            keyword: Keyword to search for
            search_fields: List of fields to search (default: ['subject', 'body'])
        """
        if not self.loaded:
            self.load()
        
        if search_fields is None:
            search_fields = ['subject', 'body']
        
        keyword_lower = keyword.lower()
        results = []
        
        for email in self.emails:
            for field in search_fields:
                if field in email and keyword_lower in str(email[field]).lower():
                    results.append(email)
                    break
        
        return results
    
    def get_all_senders(self) -> List[str]:
        """Get list of all unique senders."""
        if not self.loaded:
            self.load()
        return sorted(list(set(e.get('sender', '') for e in self.emails if e.get('sender'))))
    
    def get_all_receivers(self) -> List[str]:
        """Get list of all unique receivers."""
        if not self.loaded:
            self.load()
        receivers = set()
        for email in self.emails:
            receivers.update(email.get('receiver', []))
        return sorted(list(receivers))
    
    def get_email_count(self) -> int:
        """Get total number of emails."""
        if not self.loaded:
            self.load()
        return len(self.emails)
    
    def get_date_range(self) -> tuple:
        """Get the date range of emails (earliest, latest)."""
        if not self.loaded:
            self.load()
        
        dates = [e.get('parsed_timestamp') for e in self.emails if e.get('parsed_timestamp')]
        if not dates:
            return None, None
        
        return min(dates), max(dates)
