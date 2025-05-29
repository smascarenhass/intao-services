import logging
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class SparksAppService:
    def __init__(self):
        self.api_url = "https://internal.intao.app/api/cockpit/spark-app/users"
        
    async def get_users(self):
        """Get all users from Sparks App API"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{current_time}] Fetching users from Sparks App...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url) as response:
                    if response.status == 200:
                        users = await response.json()
                        logger.info(f"Successfully retrieved {len(users)} users from Sparks App")
                        return users
                    else:
                        error_msg = f"Failed to fetch users. Status code: {response.status}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                        
        except Exception as e:
            logger.error(f"Error fetching users from Sparks App: {str(e)}", exc_info=True)
            raise

# For backward compatibility
async def get_sparks_app_users():
    service = SparksAppService()
    return await service.get_users()
