import mysql.connector
from datetime import datetime, timedelta
import schedule
import time
from config import db_config, contatos
from whatsapp import enviar_mensagem

def buscar_chamados():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    hoje = datetime.now()
    primeiro_dia_mes_passado = (hoje.replace(day=1) - timedelta(days=1)).replace(day=1)
    ultimo_dia_mes_passado = hoje.replace(day=1) - timedelta(days=1)

    query = f"""
        SELECT NomeCli, DataEmissao, DataValidade, ValorTotal, ValorLiquido, DescontoP, Status
        FROM vw_grid_cv_vendas_cab_01
        WHERE DataEmissao = CURDATE() - INTERVAL 4 WEEK
    """

    cursor.execute(query)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados

def formatar_mensagem(chamados):
    if not chamados:
        return "Nenhuma proposta registrada no último mês."

    mensagem = "📊 *Resumo de Propostas do Último Mês*\n\n"
    for i, c in enumerate(chamados, start=1):
        emissao = c['DataEmissao'].strftime('%d/%m/%Y') if c['DataEmissao'] else '—'
        validade = c['DataValidade'].strftime('%d/%m/%Y') if c['DataValidade'] else '—'

        mensagem += (
            f"🔹 *{i}. {c['NomeCli']}*\n"
            f"📅 Emissão: {emissao}\n"
            f"💰 Valor Total: R$ {c['ValorTotal'] or 0:.2f}\n"
            f"💵 Valor Líquido: R$ {c['ValorLiquido'] or 0:.2f}\n"
            f"🔻 Desconto: {c['DescontoP'] or 0}%\n"
            f"📍 Status: {c['Status'] or '—'}\n\n"
        )
    return mensagem


def enviar_relatorio():
    chamados = buscar_chamados()
    mensagem = formatar_mensagem(chamados)
    for numero in contatos:
        enviar_mensagem(numero, mensagem)

# Agenda para rodar todos os dias às 8h
schedule.every().day.at("08:00").do(enviar_relatorio)

if __name__ == "__main__":
    print("⏰ Serviço de envio de relatórios iniciado. Aguardando o horário agendado...")
    while True:
        schedule.run_pending()
        time.sleep(60)
