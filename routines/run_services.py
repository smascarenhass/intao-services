from service_manager import ServiceManager
from workers.sync_membership_passwords_to_sparks import sync_membership_passwords_to_sparks
import time
import os
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Create a service manager instance
    manager = ServiceManager()

    # Sync Membership passwords every minute
    manager.add_service(
        name="sync_membership_passwords_to_sparks",
        function=sync_membership_passwords_to_sparks,
        interval=60  # 1 minute in seconds (sufficient for less than 250 users, without stressing the databases)
    )

    # Start the service manager
    logger.info("Starting service manager...")
    manager.start()

    try:
        # Keep the program running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping service manager...")
        manager.stop()
        logger.info("Service manager stopped.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        manager.stop()
        raise

if __name__ == "__main__":
    main()