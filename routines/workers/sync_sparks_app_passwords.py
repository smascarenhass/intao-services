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
from sqlalchemy import text

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
    Service that synchronizes passwords from Membership Pro to Sparks App.
    Makes sure users that exist in both systems have the same password as in Membership Pro.
    """
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        main_logger.info(f"Starting password synchronization at {current_time}")

        # Initialize services
        db = SessionLocal()
        membership_service = MembershipProService()
        sparks_service = SparksAppService()

        try:
            # Fetch WordPress Membership users
            membership_logger.info("=== MEMBERSHIP USERS START ===")
            membership_users = await membership_service.list_users(db)
            membership_logger.info(f"Total Membership users: {len(membership_users)}")
            
            # Convert membership users to dictionary format
            membership_users_dict = [
                {
                    "email": user.user_email.lower(),
                    "password": user.user_pass
                }
                for user in membership_users
            ]
            
            # Use the sync_passwords method from SparksAppService
            stats = sparks_service.sync_passwords(membership_users_dict)
            
            # Print summary
            main_logger.info("\n" + "="*80)
            main_logger.info("PASSWORD SYNCHRONIZATION SUMMARY")
            main_logger.info("="*80)
            
            # Overall statistics
            main_logger.info("\n📊 OVERALL STATISTICS:")
            main_logger.info(f"Total Membership users: {stats['total_membership_users']}")
            main_logger.info(f"Total Sparks users: {stats['total_sparks_users']}")
            main_logger.info(f"Total matching users: {stats['matching_users']}")
            main_logger.info(f"Updated Sparks passwords: {stats['updated_passwords']}")
            main_logger.info(f"Errors during sync: {stats['errors']}")
            
            main_logger.info("\n" + "="*80)
            main_logger.info("SYNCHRONIZATION COMPLETED")
            main_logger.info("="*80 + "\n")

        finally:
            db.close()

        # Log successful operation
        main_logger.info("Password synchronization completed successfully")
        
    except Exception as e:
        main_logger.error(f"Error during password synchronization: {str(e)}")
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
