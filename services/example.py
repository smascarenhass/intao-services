from service_manager import ServiceManager
import time

# Exemplo de funções que podem ser executadas como serviços
def exemplo_servico_1():
    print("Executando serviço 1...")
    # Aqui vai o código do seu serviço
    time.sleep(2)  # Simulando algum processamento
    print("Serviço 1 concluído!")

def exemplo_servico_2(parametro1, parametro2):
    print(f"Executando serviço 2 com parâmetros: {parametro1}, {parametro2}")
    # Aqui vai o código do seu serviço
    time.sleep(1)  # Simulando algum processamento
    print("Serviço 2 concluído!")

def main():
    # Criando uma instância do gerenciador de serviços
    manager = ServiceManager()

    # Adicionando serviços
    # Serviço que roda a cada 5 segundos
    manager.add_service(
        name="servico_periodico",
        function=exemplo_servico_1,
        interval=5
    )

    # Serviço que roda em um horário específico
    manager.add_service(
        name="servico_agendado",
        function=exemplo_servico_2,
        schedule_time="14:30",
        parametro1="valor1",
        parametro2="valor2"
    )

    # Iniciando o gerenciador de serviços
    manager.start()

    try:
        # Mantém o programa rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Para o gerenciador quando o usuário pressionar Ctrl+C
        manager.stop()

if __name__ == "__main__":
    main() 