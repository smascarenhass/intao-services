from service_manager import ServiceManager
from membership_monitor import monitor_membership_users
import time
import os
import logging

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Criando uma instância do gerenciador de serviços
    manager = ServiceManager()

    # Monitoramento de usuários do Membership Pro a cada 30 minutos
    manager.add_service(
        name="membership_monitor",
        function=monitor_membership_users,
        interval=5  # 1800 segundos = 30 minutos
    )

    # Iniciando o gerenciador de serviços
    logger.info("Iniciando gerenciador de serviços...")
    manager.start()

    try:
        # Mantém o programa rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Parando gerenciador de serviços...")
        manager.stop()
        logger.info("Gerenciador de serviços parado.")
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        manager.stop()
        raise

if __name__ == "__main__":
    main() 