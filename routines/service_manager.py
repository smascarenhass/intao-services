import time
import threading
import logging
import asyncio
from datetime import datetime
from typing import Dict, Callable, Any
import schedule
import inspect

# Configuração do logging
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
        Adiciona um serviço ao gerenciador
        
        Args:
            name: Nome do serviço
            function: Função a ser executada
            interval: Intervalo em segundos entre execuções
        """
        self.services[name] = {
            'function': function,
            'interval': interval,
            'last_run': None,
            'is_async': inspect.iscoroutinefunction(function)
        }
        logger.info(f"Serviço '{name}' adicionado com sucesso")

    def remove_service(self, name: str):
        """Remove um serviço do gerenciador."""
        if name in self.services:
            del self.services[name]
            logger.info(f"Serviço '{name}' removido com sucesso")
        else:
            logger.warning(f"Serviço '{name}' não encontrado")

    def _run_service(self, name: str):
        """Executa um serviço específico em loop"""
        service = self.services[name]
        
        if service['is_async']:
            # Criar um novo event loop para esta thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.loops[name] = loop
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # Verifica se é hora de executar o serviço
                if (service['last_run'] is None or 
                    (current_time - service['last_run']).total_seconds() >= service['interval']):
                    
                    logger.info(f"Executando serviço '{name}'...")
                    
                    if service['is_async']:
                        # Executa a função assíncrona
                        loop = self.loops[name]
                        loop.run_until_complete(service['function']())
                    else:
                        # Executa a função síncrona
                        service['function']()
                    
                    service['last_run'] = current_time
                    logger.info(f"Serviço '{name}' executado com sucesso")
                
                # Aguarda um pouco antes de verificar novamente
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao executar serviço '{name}': {str(e)}")
                time.sleep(service['interval'])  # Aguarda o intervalo antes de tentar novamente

    def start(self):
        """Inicia todos os serviços"""
        if self.running:
            logger.warning("Gerenciador de serviços já está em execução")
            return
            
        self.running = True
        logger.info("Gerenciador de serviços iniciado")
        
        # Inicia uma thread para cada serviço
        for name in self.services:
            thread = threading.Thread(target=self._run_service, args=(name,))
            thread.daemon = True
            thread.start()
            self.threads[name] = thread

    def stop(self):
        """Para todos os serviços"""
        if not self.running:
            logger.warning("Gerenciador de serviços já está parado")
            return
            
        self.running = False
        logger.info("Parando gerenciador de serviços...")
        
        # Fecha todos os event loops
        for name, loop in self.loops.items():
            loop.close()
            logger.info(f"Event loop do serviço '{name}' finalizado")
        
        # Aguarda todas as threads terminarem
        for name, thread in self.threads.items():
            thread.join(timeout=5)
            logger.info(f"Thread do serviço '{name}' finalizada")
            
        self.threads.clear()
        self.loops.clear()
        logger.info("Gerenciador de serviços parado")

    def get_service_status(self, name: str = None):
        """Retorna o status de um serviço específico ou de todos os serviços."""
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