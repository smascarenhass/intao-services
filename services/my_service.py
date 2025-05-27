import time
from datetime import datetime

def monitor_system():
    """Serviço que monitora o sistema a cada minuto"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] Monitorando sistema...")
    # Aqui você pode adicionar sua lógica de monitoramento
    # Por exemplo: verificar uso de CPU, memória, etc.

def backup_database():
    """Serviço que faz backup do banco de dados diariamente"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] Iniciando backup do banco de dados...")
    # Aqui você pode adicionar sua lógica de backup
    time.sleep(2)  # Simulando o processo de backup
    print(f"[{current_time}] Backup concluído com sucesso!")

def cleanup_temp_files():
    """Serviço que limpa arquivos temporários a cada hora"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] Limpando arquivos temporários...")
    # Aqui você pode adicionar sua lógica de limpeza
    time.sleep(1)  # Simulando o processo de limpeza
    print(f"[{current_time}] Limpeza concluída!") 