# agendador.py
import time
from datetime import datetime
import pytz

# Importa a função principal do seu script
from main import consultar_e_enviar_resumo_mensal

# Fuso horário de Brasília
brasilia_tz = pytz.timezone("America/Sao_Paulo")

ultima_execucao = None

def job():
    agora = datetime.now(brasilia_tz)
    print(f"🕗 Executando envio de resumo às {agora.strftime('%H:%M:%S')} (Horário de Brasília)")
    consultar_e_enviar_resumo_mensal()

def loop_agendado():
    print("✅ Agendamento diário ativo (Horário de Brasília)")

    global ultima_execucao
    while True:
        agora = datetime.now(brasilia_tz)
        # Executa apenas uma vez por dia às 08:00
        if agora.hour == 8 and agora.minute == 0:
            if ultima_execucao != agora.date():
                job()
                ultima_execucao = agora.date()
        time.sleep(10)  # verifica a cada 10 segundos

if __name__ == "__main__":
    loop_agendado()
