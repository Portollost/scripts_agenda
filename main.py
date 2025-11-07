import mysql.connector
from datetime import datetime, timedelta
import schedule
import time
from config import db_config, contatos
from whatsapp import enviar_mensagem


def buscar_chamados():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Data de 30 dias atrás
    data_alvo = (datetime.now() - timedelta(days=30)).date()

    query = """
        SELECT 
            v.CodVendasCab,
            v.CodCli,
            v.CodCliContato,
            v.DataEmissao,
            v.Status,
            v.Ambientes,
            c.NomeCli,
            c.Logradouro,
            c.Numero,
            c.Complemento,
            c.Bairro,
            c.Cidade,
            c.UF,
            cc.CelularCliContato01,
            cc.CelularCliContato02,
            cc.TelefoneFixoContato,
            cc.EmailContato
        FROM vw_obras_ambientes v
        LEFT JOIN C_Clientes c ON v.CodCli = c.CodCli
        LEFT JOIN C_CliContatos cc ON v.CodCliContato = cc.CodCliContato
        WHERE v.Status = 'A_CONFIRMAR'
            AND DATE(v.DataEmissao) <= CURDATE() - INTERVAL 30 DAY
    """

    cursor.execute(query)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados


def formatar_mensagem(chamados):
    if not chamados:
        return "Nenhuma proposta com status 'A_CONFIRMAR' há 30 dias."

    mensagem = "📋 *Propostas pendentes de confirmação (30 dias)*\n\n"
    for c in chamados:
        emissao = c['DataEmissao'].strftime('%d/%m/%Y') if c['DataEmissao'] else '—'
        endereco = f"{c['Logradouro'] or ''}, {c['Numero'] or ''} {c['Complemento'] or ''}, {c['Bairro'] or ''}, {c['Cidade'] or ''} - {c['UF'] or ''}".strip().replace(" ,", ",")
        mensagem += (
            f"📑 *Número da proposta:* {c['CodVendasCab']}\n"
            f"📅 *Data Solicitação:* {emissao}\n"
            f"👤 *Nome do cliente:* {c['NomeCli'] or '—'}\n"
            f"🏠 *Endereço cliente:* {endereco}\n"
            f"📞 *Contato cliente:*\n"
            f"  • Celular 1: {c['CelularCliContato01'] or '—'}\n"
            f"  • Celular 2: {c['CelularCliContato02'] or '—'}\n"
            f"  • Telefone Fixo: {c['TelefoneFixoContato'] or '—'}\n"
            f"  • E-mail: {c['EmailContato'] or '—'}\n"
            f"🧱 *Demanda da proposta:* {c['Ambientes'] or '—'}\n"
            f"📍 *Status:* {c['Status'] or '—'}\n"
            f"{'-'*40}\n"
        )
    return mensagem


def enviar_relatorio():
    chamados = buscar_chamados()
    mensagem = formatar_mensagem(chamados)
    for numero in contatos:
        enviar_mensagem(numero, mensagem)

enviar_relatorio()

# Agenda para rodar todos os dias às 8h
schedule.every().day.at("08:00").do(enviar_relatorio)

if __name__ == "__main__":
    print("⏰ Serviço de envio de propostas pendentes iniciado. Aguardando o horário agendado...")
    while True:
        schedule.run_pending()
        time.sleep(60)
