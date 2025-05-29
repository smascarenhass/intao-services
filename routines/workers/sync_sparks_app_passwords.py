import logging
from datetime import datetime
import asyncio
import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

from api.services.database import SessionLocal
from api.services.membership_pro import MembershipProService
from routines.services.sparks_app import SparksAppService

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create specific loggers for each service
membership_logger = logging.getLogger('membership_sync')
sparks_logger = logging.getLogger('sparks_sync')
main_logger = logging.getLogger('sync_service')

async def sync_sparks_app_passwords():
    """
    Service that synchronizes the members database.
    Performs synchronization between local and remote databases.
    """
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        main_logger.info(f"Starting members database synchronization at {current_time}")

        # Initialize services
        db = SessionLocal()
        membership_service = MembershipProService()
        sparks_service = SparksAppService()

        try:
            # Fetch WordPress Membership users
            membership_logger.info("=== MEMBERSHIP USERS START ===")
            membership_users = await membership_service.list_users(db)
            membership_logger.info(f"Total Membership users: {len(membership_users)}")
            
            # Create a dictionary of membership users by email
            membership_users_dict = {user.user_email.lower(): user for user in membership_users}
            
            # Fetch Sparks App users
            sparks_logger.info("=== SPARKS USERS START ===")
            sparks_users = await sparks_service.get_users()
            sparks_logger.info(f"Total Sparks users: {len(sparks_users)}")
            
            # Find matching users
            matching_users = []
            for sparks_user in sparks_users:
                sparks_email = sparks_user.get('email', '').lower()
                if sparks_email in membership_users_dict:
                    membership_user = membership_users_dict[sparks_email]
                    matching_users.append({
                        'email': sparks_email,
                        'display_name': membership_user.display_name,
                        'membership_id': membership_user.ID,
                        'app_password': sparks_user.get('app_password', 'N/A'),
                        'membership_status': membership_user.user_status
                    })
            
            # Log matching users
            main_logger.info("=== MATCHING USERS START ===")
            main_logger.info(f"Total matching users: {len(matching_users)}")
            for user in matching_users:
                main_logger.info(f"""
                User: {user['display_name']}
                Email: {user['email']}
                Membership ID: {user['membership_id']}
                App Password: {user['app_password']}
                Status: {user['membership_status']}
                ------------------------
                """)
            main_logger.info("=== MATCHING USERS END ===\n")

        finally:
            db.close()

        # Log successful operation
        main_logger.info("Members database synchronization completed successfully")
        
    except Exception as e:
        main_logger.error(f"Error during members database synchronization: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(sync_sparks_app_passwords())

def get_last_sync_time():
    """Returns the timestamp of the last synchronization"""
    # TODO: Implement logic to store and retrieve timestamp
    pass

def resolve_conflicts(local_data, remote_data):
    """Resolves conflicts between local and remote data"""
    # TODO: Implement conflict resolution logic
    pass
