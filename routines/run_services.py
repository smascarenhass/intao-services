from service_manager import ServiceManager
from workers.sync_sparks_app_passwords import sync_sparks_app_passwords
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

    # Sync Membership Database a cada 20 segundos
    manager.add_service(
        name="sync_sparks_app_passwords",
        function=sync_sparks_app_passwords,
        interval=20  # 20 segundos
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