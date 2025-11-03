import time
from datetime import datetime
import pytz

# Importa sua função principal
from main import enviar_relatorio

# Fuso horário de Brasília
brasilia_tz = pytz.timezone("America/Sao_Paulo")

ultima_execucao = None

def job():
    agora = datetime.now(brasilia_tz)
    print(f"🕗 Executando job às {agora.strftime('%H:%M:%S')} (Horário de Brasília)")
    try:
        enviar_relatorio()
        print(f"✅ Relatórios enviados com sucesso em {agora.strftime('%d/%m/%Y %H:%M')}")
    except Exception as e:
        print(f"❌ Erro ao executar job: {e}")

def loop_agendado():
    print("✅ Agendamento diário ativo (Horário de Brasília)")
    global ultima_execucao

    while True:
        agora = datetime.now(brasilia_tz)
        # Executa apenas uma vez por dia, às 08:00
        if agora.hour == 18 and agora.minute == 45:
            if ultima_execucao != agora.date():
                job()
                ultima_execucao = agora.date()

        time.sleep(10)  # checa a cada 10 segundos

if __name__ == "__main__":
    loop_agendado()
