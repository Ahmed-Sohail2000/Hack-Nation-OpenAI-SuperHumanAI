"""
AI Chief of Staff - Main interface for querying organizational intelligence.
"""
import os
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

from src.data_loader import EmailDataLoader
from src.organizational_intelligence import OrganizationalIntelligence

load_dotenv()


class AICChiefOfStaff:
    """AI Chief of Staff for Organizational Intelligence."""
    
    def __init__(self, json_file_path: str = "emails.json", api_key: Optional[str] = None):
        """
        Initialize the AI Chief of Staff.
        
        Args:
            json_file_path: Path to email JSON file
            api_key: OpenAI API key (if not provided, uses OPENAI_API_KEY env var)
        """
        self.data_loader = EmailDataLoader(json_file_path)
        self.org_intelligence = OrganizationalIntelligence(self.data_loader)
        
        # Initialize OpenAI client
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in .env file.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    def _prepare_context(self, query: str) -> str:
        """
        Prepare context about the organization for the AI.
        
        Args:
            query: User query
            
        Returns:
            Context string with organizational information
        """
        insights = self.org_intelligence.get_organizational_insights()
        
        context = f"""Organizational Intelligence Context:

Total Emails: {insights['total_emails']}
Unique Senders: {insights['unique_senders']}
Unique Receivers: {insights['unique_receivers']}
Date Range: {insights['date_range']['earliest']} to {insights['date_range']['latest']}

Top Communicators:
"""
        for email, count in insights['top_communicators'][:5]:
            context += f"  - {email}: {count} communications\n"
        
        return context
    
    def _get_relevant_emails(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get relevant emails based on query.
        
        Args:
            query: User query
            limit: Maximum number of emails to return
            
        Returns:
            List of relevant email dictionaries
        """
        # Simple keyword-based search
        keywords = query.lower().split()
        relevant_emails = []
        
        for keyword in keywords:
            if len(keyword) > 3:  # Skip very short words
                emails = self.data_loader.get_emails_by_keyword(keyword)
                relevant_emails.extend(emails)
        
        # Remove duplicates and limit
        # Use a hash of email content to identify duplicates
        seen = set()
        unique_emails = []
        for email in relevant_emails:
            # Create unique identifier from email content
            email_key = (
                email.get('sender', ''),
                tuple(sorted(email.get('receiver', []))),
                email.get('subject', ''),
                email.get('timestamp', '')
            )
            if email_key not in seen:
                seen.add(email_key)
                unique_emails.append(email)
                if len(unique_emails) >= limit:
                    break
        
        return unique_emails
    
    def query(self, user_query: str, include_emails: bool = True) -> Dict[str, Any]:
        """
        Query the AI Chief of Staff.
        
        Args:
            user_query: User's question or request
            include_emails: Whether to include relevant emails in context
            
        Returns:
            Dictionary with AI response and metadata
        """
        # Prepare context
        context = self._prepare_context(user_query)
        
        # Get relevant emails if requested
        relevant_emails = []
        if include_emails:
            relevant_emails = self._get_relevant_emails(user_query, limit=5)
        
        # Build email context
        email_context = ""
        if relevant_emails:
            email_context = "\n\nRelevant Emails:\n"
            for i, email in enumerate(relevant_emails[:5], 1):
                email_context += f"\nEmail {i}:\n"
                email_context += f"From: {email.get('sender', 'Unknown')}\n"
                email_context += f"To: {', '.join(email.get('receiver', []))}\n"
                email_context += f"Subject: {email.get('subject', 'No subject')}\n"
                email_context += f"Date: {email.get('timestamp', 'Unknown')}\n"
                body_preview = email.get('body', '')[:500]
                email_context += f"Body: {body_preview}...\n"
        
        # Create prompt
        system_prompt = """You are an AI Chief of Staff for Organizational Intelligence. 
Your role is to analyze organizational communications and provide insights, answer questions, 
and help understand patterns, relationships, and dynamics within the organization.

You have access to email communications data. Use this information to provide accurate, 
helpful, and insightful responses. Be concise but thorough."""
        
        user_prompt = f"""{context}{email_context}

User Query: {user_query}

Please provide a comprehensive answer based on the organizational intelligence data available."""
        
        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                "query": user_query,
                "response": ai_response,
                "relevant_emails_count": len(relevant_emails),
                "model": self.model
            }
        
        except Exception as e:
            return {
                "query": user_query,
                "response": f"Error processing query: {str(e)}",
                "error": True
            }
    
    def get_insights(self) -> Dict[str, Any]:
        """
        Get organizational insights summary.
        
        Returns:
            Dictionary with organizational insights
        """
        return self.org_intelligence.get_organizational_insights()
    
    def analyze_person(self, email_address: str) -> Dict[str, Any]:
        """
        Analyze communication patterns for a specific person.
        
        Args:
            email_address: Email address of the person
            
        Returns:
            Dictionary with person's communication patterns
        """
        patterns = self.org_intelligence.get_communication_patterns(email_address)
        
        # Get AI analysis
        query = f"Analyze the communication patterns and role of {email_address} in the organization."
        ai_analysis = self.query(query, include_emails=False)
        
        return {
            "email": email_address,
            "patterns": patterns,
            "ai_analysis": ai_analysis.get("response", "")
        }
