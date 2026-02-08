"""
Main application entry point for AI Chief of Staff.
"""
import os
from dotenv import load_dotenv
from src.ai_chief_of_staff import AICChiefOfStaff

load_dotenv()


def main():
    """Main CLI interface for AI Chief of Staff."""
    print("=" * 60)
    print("AI Chief of Staff for Organizational Intelligence")
    print("=" * 60)
    print()
    
    # Initialize
    json_file = os.getenv("JSON_FILE_PATH", "emails.json")
    
    try:
        chief = AICChiefOfStaff(json_file_path=json_file)
        print(f"✓ Loaded {chief.data_loader.get_email_count()} emails")
        print()
        
        # Interactive mode
        print("Enter your queries (type 'exit' to quit, 'insights' for summary):")
        print()
        
        while True:
            query = input("Query: ").strip()
            
            if not query:
                continue
            
            if query.lower() == 'exit':
                print("Goodbye!")
                break
            
            if query.lower() == 'insights':
                insights = chief.get_insights()
                print("\nOrganizational Insights:")
                print(f"  Total Emails: {insights['total_emails']}")
                print(f"  Unique Senders: {insights['unique_senders']}")
                print(f"  Unique Receivers: {insights['unique_receivers']}")
                print("\nTop Communicators:")
                for email, count in insights['top_communicators'][:5]:
                    print(f"  - {email}: {count} communications")
                print()
                continue
            
            print("\nThinking...")
            result = chief.query(query)
            print(f"\n{result['response']}\n")
            if result.get('relevant_emails_count', 0) > 0:
                print(f"(Based on {result['relevant_emails_count']} relevant emails)\n")
    
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set OPENAI_API_KEY in your .env file")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure emails.json exists. Run process_emails.py first.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
