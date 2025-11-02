import mysql.connector
from datetime import datetime
import requests
from whatsapp import get_headers, get_number_id

# ==========================
# CONFIGURAÇÕES
# ==========================    

db_config = {
    'host': '187.73.33.163',
    'user': 'eugon1',
    'password': 'Master45@net',
    'database': 'eugon1'
}

contatos_resumo_confirmar = [
    "553171538434",
    "553187014538",
    "553172079788",
    "553182657231"
]

# ==========================
# FUNÇÕES AUXILIARES
# ==========================

def enviar_mensagem_texto(numero, mensagem):
    headers = get_headers()
    number_id = get_number_id()
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensagem}
    }
    try:
        r = requests.post(f"https://graph.facebook.com/v17.0/{number_id}/messages",
                          headers=headers, json=payload)
        if r.status_code == 200:
            print(f"✅ Mensagem enviada para {numero}")
        else:
            print(f"❌ Erro ao enviar mensagem para {numero}: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Erro ao conectar com a API WhatsApp: {e}")

def enviar_mensagem_texto_em_blocos(numero, mensagem, bloco_max=4000):
    for i in range(0, len(mensagem), bloco_max):
        bloco = mensagem[i:i+bloco_max]
        enviar_mensagem_texto(numero, bloco)

# ==========================
# FUNÇÃO PRINCIPAL
# ==========================

def consultar_e_enviar_resumo_mensal():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Query exata fornecida
    query = """
    SELECT id, title, start_date, relatorio, CodStatus
    FROM calendar
    WHERE start_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
      AND CodStatus = 1
    ORDER BY start_date ASC;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    if not rows:
        print("⚠️ Nenhum registro pendente no último mês.")
        cursor.close()
        conn.close()
        return

    # Atualiza CodStatus para 2 ("Confirmado" ou outro status desejado)
    update_query = "UPDATE calendar SET CodStatus = %s WHERE id = %s"
    for row in rows:
        cursor.execute(update_query, (2, row["id"]))
    conn.commit()
    print(f"✅ {len(rows)} registros atualizados para 'Confirmado'.")

    # Monta resumo bonito
    texto_resumo = f"📋 *Resumo do último mês - Registros Pendentes:*\n\n"
    for i, r in enumerate(rows, start=1):
        titulo = r["title"] or "Sem título"
        data = r["start_date"].strftime("%d/%m/%Y") if r["start_date"] else "-"
        descricao = r["relatorio"] or "Sem descrição"
        texto_resumo += (
            f"🔹 *{titulo}*\n"
            f"🗓️ Data: {data}\n"
            f"📝 Descrição: {descricao}\n"
            f"⚠️ Status: Pendente\n\n"
        )

    # Envia para todos os contatos, dividindo em blocos se necessário
    for numero in contatos_resumo_confirmar:
        enviar_mensagem_texto_em_blocos(numero, texto_resumo)

    cursor.close()
    conn.close()
    print("📤 Resumo mensal enviado com sucesso.")

# ==========================
# EXECUÇÃO DIRETA
# ==========================

if __name__ == "__main__":
    consultar_e_enviar_resumo_mensal()
