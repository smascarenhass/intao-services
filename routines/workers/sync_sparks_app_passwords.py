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
            
            # Create a dictionary of membership users by email
            membership_users_dict = {user.user_email.lower(): user for user in membership_users}
            
            # Fetch Sparks App users
            sparks_logger.info("=== SPARKS USERS START ===")
            sparks_users = sparks_service.get_sparks_users()
            sparks_logger.info(f"Total Sparks users: {len(sparks_users)}")
            
            # Track synchronization statistics
            total_matches = 0
            updated_sparks = 0
            errors = 0
            
            # Process matching users
            for sparks_user in sparks_users:
                sparks_email = sparks_user.get('email', '').lower()
                if sparks_email in membership_users_dict:
                    total_matches += 1
                    membership_user = membership_users_dict[sparks_email]
                    
                    try:
                        # Get current passwords
                        membership_pass = membership_user.user_pass
                        sparks_pass = sparks_user.get('password', 'N/A')
                        
                        # If passwords are different, update Sparks password
                        if sparks_pass != membership_pass:
                            try:
                                # Truncate password to 60 characters to match database field size
                                truncated_password = membership_pass[:60]
                                
                                # Update password in Sparks App database
                                query = text("""
                                    UPDATE users 
                                    SET password = :password 
                                    WHERE email = :email
                                """)
                                sparks_service.sparks_session.execute(
                                    query, 
                                    {
                                        "password": truncated_password,
                                        "email": sparks_email
                                    }
                                )
                                sparks_service.sparks_session.commit()
                                
                                updated_sparks += 1
                                sparks_logger.info(f"Updated Sparks password for user: {sparks_email}")
                            except Exception as e:
                                sparks_service.sparks_session.rollback()
                                errors += 1
                                sparks_logger.error(f"Failed to update Sparks password for user {sparks_email}: {str(e)}")
                    
                    except Exception as e:
                        errors += 1
                        main_logger.error(f"Error processing user {sparks_email}: {str(e)}")

            # Print summary
            main_logger.info("\n" + "="*80)
            main_logger.info("PASSWORD SYNCHRONIZATION SUMMARY")
            main_logger.info("="*80)
            
            # Overall statistics
            main_logger.info("\n📊 OVERALL STATISTICS:")
            main_logger.info(f"Total Membership users: {len(membership_users)}")
            main_logger.info(f"Total Sparks users: {len(sparks_users)}")
            main_logger.info(f"Total matching users: {total_matches}")
            main_logger.info(f"Updated Sparks passwords: {updated_sparks}")
            main_logger.info(f"Errors during sync: {errors}")
            
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
