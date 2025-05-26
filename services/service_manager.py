import time
import threading
import logging
from datetime import datetime
from typing import Dict, Callable, Any
import schedule

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceManager:
    def __init__(self):
        self.services: Dict[str, Dict[str, Any]] = {}
        self.running = False
        self.thread = None

    def add_service(self, name: str, function: Callable, interval: int = None, 
                   schedule_time: str = None, **kwargs):
        """
        Adiciona um novo serviço ao gerenciador.
        
        Args:
            name: Nome único do serviço
            function: Função a ser executada
            interval: Intervalo em segundos para execução periódica (opcional)
            schedule_time: Horário específico para execução (formato HH:MM) (opcional)
            **kwargs: Argumentos adicionais para a função
        """
        if name in self.services:
            raise ValueError(f"Serviço com nome '{name}' já existe")

        service_info = {
            'function': function,
            'interval': interval,
            'schedule_time': schedule_time,
            'kwargs': kwargs,
            'last_run': None,
            'is_running': False
        }
        
        self.services[name] = service_info
        logger.info(f"Serviço '{name}' adicionado com sucesso")

    def remove_service(self, name: str):
        """Remove um serviço do gerenciador."""
        if name in self.services:
            del self.services[name]
            logger.info(f"Serviço '{name}' removido com sucesso")
        else:
            logger.warning(f"Serviço '{name}' não encontrado")

    def run_service(self, name: str):
        """Executa um serviço específico."""
        if name not in self.services:
            logger.error(f"Serviço '{name}' não encontrado")
            return

        service = self.services[name]
        if service['is_running']:
            logger.warning(f"Serviço '{name}' já está em execução")
            return

        try:
            service['is_running'] = True
            service['last_run'] = datetime.now()
            logger.info(f"Iniciando execução do serviço '{name}'")
            service['function'](**service['kwargs'])
            logger.info(f"Serviço '{name}' executado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao executar serviço '{name}': {str(e)}")
        finally:
            service['is_running'] = False

    def _run_scheduled_services(self):
        """Executa os serviços agendados."""
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def start(self):
        """Inicia o gerenciador de serviços."""
        if self.running:
            logger.warning("Gerenciador de serviços já está em execução")
            return

        self.running = True
        
        # Configura os serviços agendados
        for name, service in self.services.items():
            if service['interval']:
                schedule.every(service['interval']).seconds.do(self.run_service, name)
            elif service['schedule_time']:
                schedule.every().day.at(service['schedule_time']).do(self.run_service, name)

        # Inicia a thread de execução dos serviços agendados
        self.thread = threading.Thread(target=self._run_scheduled_services)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("Gerenciador de serviços iniciado")

    def stop(self):
        """Para o gerenciador de serviços."""
        if not self.running:
            logger.warning("Gerenciador de serviços não está em execução")
            return

        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Gerenciador de serviços parado")

    def get_service_status(self, name: str = None):
        """Retorna o status de um serviço específico ou de todos os serviços."""
        if name:
            if name in self.services:
                service = self.services[name]
                return {
                    'name': name,
                    'is_running': service['is_running'],
                    'last_run': service['last_run'],
                    'interval': service['interval'],
                    'schedule_time': service['schedule_time']
                }
            return None
        
        return {
            name: {
                'is_running': service['is_running'],
                'last_run': service['last_run'],
                'interval': service['interval'],
                'schedule_time': service['schedule_time']
            }
            for name, service in self.services.items()
        } 