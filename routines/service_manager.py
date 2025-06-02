import time
import threading
import logging
import asyncio
from datetime import datetime
from typing import Dict, Callable, Any
import schedule
import inspect

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceManager:
    def __init__(self):
        self.services: Dict[str, dict] = {}
        self.running = False
        self.threads: Dict[str, threading.Thread] = {}
        self.loops: Dict[str, asyncio.AbstractEventLoop] = {}

    def add_service(self, name: str, function: Callable, interval: int):
        """
        Adds a service to the manager
        
        Args:
            name: Service name
            function: Function to be executed
            interval: Interval in seconds between executions
        """
        self.services[name] = {
            'function': function,
            'interval': interval,
            'last_run': None,
            'is_async': inspect.iscoroutinefunction(function)
        }
        logger.info(f"Service '{name}' added successfully")

    def remove_service(self, name: str):
        """Removes a service from the manager."""
        if name in self.services:
            del self.services[name]
            logger.info(f"Service '{name}' removed successfully")
        else:
            logger.warning(f"Service '{name}' not found")

    def _run_service(self, name: str):
        """Executes a specific service in a loop"""
        service = self.services[name]
        
        if service['is_async']:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.loops[name] = loop
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check if it's time to execute the service
                if (service['last_run'] is None or 
                    (current_time - service['last_run']).total_seconds() >= service['interval']):
                    
                    logger.info(f"Executing service '{name}'...")
                    
                    if service['is_async']:
                        # Execute the async function
                        loop = self.loops[name]
                        loop.run_until_complete(service['function']())
                    else:
                        # Execute the sync function
                        service['function']()
                    
                    service['last_run'] = current_time
                    logger.info(f"Service '{name}' executed successfully")
                
                # Wait a bit before checking again
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error executing service '{name}': {str(e)}")
                time.sleep(service['interval'])  # Wait for the interval before trying again

    def start(self):
        """Starts all services"""
        if self.running:
            logger.warning("Service manager is already running")
            return
            
        self.running = True
        logger.info("Service manager started")
        
        # Start a thread for each service
        for name in self.services:
            thread = threading.Thread(target=self._run_service, args=(name,))
            thread.daemon = True
            thread.start()
            self.threads[name] = thread

    def stop(self):
        """Stops all services"""
        if not self.running:
            logger.warning("Service manager is already stopped")
            return
            
        self.running = False
        logger.info("Stopping service manager...")
        
        # Close all event loops
        for name, loop in self.loops.items():
            loop.close()
            logger.info(f"Event loop for service '{name}' finished")
        
        # Wait for all threads to finish
        for name, thread in self.threads.items():
            thread.join(timeout=5)
            logger.info(f"Thread for service '{name}' finished")
            
        self.threads.clear()
        self.loops.clear()
        logger.info("Service manager stopped")

    def get_service_status(self, name: str = None):
        """Returns the status of a specific service or all services."""
        if name:
            if name in self.services:
                service = self.services[name]
                return {
                    'name': name,
                    'is_running': True,
                    'last_run': service['last_run'],
                    'interval': service['interval'],
                    'is_async': service['is_async']
                }
            return None
        
        return {
            name: {
                'is_running': True,
                'last_run': service['last_run'],
                'interval': service['interval'],
                'is_async': service['is_async']
            }
            for name, service in self.services.items()
        }