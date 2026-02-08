import csv
import json
import sys
import os
from email import message_from_string
from email.utils import parsedate_to_datetime, parseaddr
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# increase field size limit of the csv
try:
    csv.field_size_limit(10_000_000)
except (OverflowError, ValueError):
    # On Windows, try a smaller value
    try:
        csv.field_size_limit(2_147_483_647)  # Max 32-bit signed int
    except (OverflowError, ValueError):
        pass  # Use default limit

def get_email_body(msg):
    """
    Extract body text from email message, handling multipart messages.
    
    Args:
        msg: Email message object
        
    Returns:
        str: Email body text
    """
    body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # Skip attachments
            if "attachment" in content_disposition:
                continue
            
            # Prefer text/plain, fallback to text/html
            if content_type == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        body = payload.decode(charset, errors='ignore')
                        break
                except Exception:
                    pass
            elif content_type == "text/html" and not body:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        body = payload.decode(charset, errors='ignore')
                except Exception:
                    pass
    else:
        # Single part message
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                body = payload.decode(charset, errors='ignore')
        except Exception:
            pass
    
    return body.strip()


def parse_email_addresses(address_string):
    """
    Parse email addresses from a string, handling multiple recipients.
    
    Args:
        address_string: String containing email addresses
        
    Returns:
        list: List of email addresses
    """
    if not address_string:
        return []
    
    addresses = []
    # Split by comma and parse each address
    for addr in address_string.split(','):
        addr = addr.strip()
        if addr:
            # Use parseaddr to extract just the email address
            name, email = parseaddr(addr)
            if email:
                addresses.append(email)
            elif addr:
                addresses.append(addr)
    
    return addresses


def parse_emails(csv_file_path, json_file_path):
    """
    Reads emails from CSV and converts them to JSON format.
    
    Args:
        csv_file_path: Path to the input CSV file
        json_file_path: Path to the output JSON file
    """
    emails = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Get the raw email message from the 'message' column
            raw_message = row.get('message', '').strip()
            
            if not raw_message:
                # Skip empty messages
                continue
            
            try:
                # Parse the raw email message
                msg = message_from_string(raw_message)
                
                # Extract sender
                from_field = msg.get('From', '').strip()
                sender = parseaddr(from_field)[1] if from_field else ''
                if not sender and from_field:
                    sender = from_field
                
                # Extract receiver(s)
                to_field = msg.get('To', '').strip()
                receiver = parse_email_addresses(to_field)
                
                # Extract subject
                subject = msg.get('Subject', '').strip()
                
                # Extract date/timestamp
                date_field = msg.get('Date', '').strip()
                timestamp = date_field  # Keep as string, or convert to ISO format if needed
                
                # Extract body
                body = get_email_body(msg)
                
                # Create email object
                email_obj = {
                    "sender": sender,
                    "receiver": receiver,
                    "subject": subject,
                    "timestamp": timestamp,
                    "body": body
                }
                
                emails.append(email_obj)
                
            except Exception as e:
                # Skip emails that can't be parsed
                print(f"Error parsing email: {e}", file=sys.stderr)
                continue
    
    # Write to JSON file
    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(emails, jsonfile, ensure_ascii=False, indent=2)


def main():
    # Get file paths from environment variables or use defaults
    csv_file = os.getenv("CSV_FILE_PATH", "emails.csv")
    json_file = os.getenv("JSON_FILE_PATH", "emails.json")
    
    parse_emails(csv_file, json_file)
    print(f"Successfully converted {csv_file} to {json_file}")


if __name__ == "__main__":
    main()
