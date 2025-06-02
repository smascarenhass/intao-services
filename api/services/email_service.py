from typing import Dict, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from jinja2 import Environment, FileSystemLoader
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "email-smtp.eu-west-1.amazonaws.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sender_email = os.getenv("SENDER_EMAIL", "support@intao.app")
        self.sender_name = "Intao"
        
        # Validate required environment variables
        if not all([self.smtp_username, self.smtp_password, self.sender_email]):
            logger.error("Missing required email configuration. Please check your environment variables.")
            raise ValueError("Missing required email configuration")
        
        # Setup Jinja2 environment for templates
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def _render_template(self, template_name: str, data: Dict) -> str:
        """Render an email template with the given data."""
        template = self.env.get_template(f"{template_name}.html")
        return template.render(**data)

    def send_email(self, to_email: str, subject: str, template_name: str, template_data: Dict) -> bool:
        """
        Send an email using the specified template and data.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            template_name: Name of the template file (without extension)
            template_data: Dictionary containing template variables
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = formataddr((self.sender_name, self.sender_email))
            msg['To'] = to_email
            msg['Subject'] = subject

            # Render template
            html_content = self._render_template(template_name, template_data)
            msg.attach(MIMEText(html_content, 'html'))

            # Connect to SMTP server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()  # Can be omitted
                server.starttls()  # Secure the connection
                server.ehlo()  # Can be omitted
                
                logger.info(f"Attempting to login to SMTP server {self.smtp_server}")
                server.login(self.smtp_username, self.smtp_password)
                
                logger.info(f"Sending email to {to_email}")
                server.send_message(msg)
                logger.info("Email sent successfully")

            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication Error: {str(e)}")
            raise Exception("Failed to authenticate with SMTP server. Please check your credentials.")
        except smtplib.SMTPException as e:
            logger.error(f"SMTP Error: {str(e)}")
            raise Exception(f"Failed to send email: {str(e)}")
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise Exception(f"Unexpected error while sending email: {str(e)}")

    def send_invitation(self, to_email: str, user_name: str, user: str, 
                       company_spaces: str, company_logo: Optional[str], 
                       welcome_message: str, link: str, language: str = 'en') -> bool:
        """
        Send an invitation email.
        
        Args:
            to_email: Recipient email address
            user_name: Name of the user sending the invitation
            user: Username of the sender
            company_spaces: Company/space name
            company_logo: URL to company logo (optional)
            welcome_message: Custom welcome message
            link: Invitation link
            language: Email language ('en' or 'de')
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        template_data = {
            'user_name': user_name,
            'user': user,
            'company_spaces': company_spaces,
            'company_logo': company_logo,
            'welcome_message': welcome_message,
            'link': link,
            'language': language
        }
        
        subject = "Start learning with Intao" if language == 'en' else "Lernen mit Intao"
        return self.send_email(to_email, subject, 'invitation', template_data) 