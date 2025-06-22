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

main_logger = logging.getLogger('sync_service')

async def sync_membership_passwords_to_sparks():
    """
    Service that synchronizes passwords from Membership Pro to Sparks App.
    For each user present in both systems, ensures the password in Sparks App matches the Membership Pro password.
    """
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        main_logger.info(f"Starting password synchronization (Membership → Sparks) at {current_time}")

        # Initialize services
        db = SessionLocal()
        membership_service = MembershipProService()
        sparks_service = SparksAppService()

        try:
            # Fetch all users from Membership Pro
            membership_users = await membership_service.list_users(db)
            # Convert to dicts for sync_passwords
            membership_users_dicts = []
            for user in membership_users:
                membership_users_dicts.append({
                    'email': user.user_email.lower(),
                    'password': user.user_pass,
                    'first_name': getattr(user, 'first_name', ''),
                    'last_name': getattr(user, 'last_name', '')
                })

            # Sync passwords to Sparks App
            stats = sparks_service.sync_passwords(membership_users_dicts)

            main_logger.info("\n" + "="*80)
            main_logger.info("MEMBERSHIP → SPARKS PASSWORD SYNCHRONIZATION SUMMARY")
            main_logger.info("="*80)
            for k, v in stats.items():
                main_logger.info(f"{k}: {v}")
            main_logger.info("="*80 + "\n")

        finally:
            db.close()

        main_logger.info("Password synchronization (Membership → Sparks) completed successfully")

    except Exception as e:
        main_logger.error(f"Error during password synchronization: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(sync_membership_passwords_to_sparks()) 