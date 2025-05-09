from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Dados do usuário
LOGIN_URL = "https://widecommerce.freshdesk.com/support/login"
TICKET_URL = "https://widecommerce.freshdesk.com/support/tickets/new"
SUBMIT_URL = "https://widecommerce.freshdesk.com/support/tickets"

EMAIL = os.getenv("EMAIL")  # Use variável de ambiente para não expor a senha
SENHA = os.getenv("SENHA")  # Use variável de ambiente para não expor a senha

# Dados do ticket
TICKET_EMAIL = "suporte.ecom@ferpam.com.br"
TICKET_SUBJECT = "teste"
TICKET_PRIORITY = "1"  # 1: Baixa, 2: Média, 3: Alta, 4: Urgente
TICKET_DESCRIPTION = "Detalhes da ocorrência: teste."

# Sessão
session = requests.Session()

# 1. Login
def login():
    resp = session.get(LOGIN_URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    token = soup.find("input", {"name": "authenticity_token"})['value']

    payload = {
        "authenticity_token": token,
        "user_session[email]": EMAIL,
        "user_session[password]": SENHA,
        "user_session[remember_me]": "0"
    }

    r = session.post(LOGIN_URL, data=payload)
    if "logout" in r.text or "Novo ticket" in r.text:
        print("✅ Login realizado com sucesso.")
    else:
        print("❌ Falha no login.")
        exit()

# 2. Criar ticket
def criar_ticket():
    r = session.get(TICKET_URL)
    soup = BeautifulSoup(r.text, 'html.parser')
    token = soup.find("input", {"name": "authenticity_token"})['value']

    payload = {
        "utf8": "✓",
        "authenticity_token": token,
        "helpdesk_ticket[email]": TICKET_EMAIL,
        "helpdesk_ticket[subject]": TICKET_SUBJECT,
        "helpdesk_ticket[priority]": TICKET_PRIORITY,
        "helpdesk_ticket[ticket_body_attributes][description_html]": TICKET_DESCRIPTION
    }

    response = session.post(SUBMIT_URL, data=payload)
    if "ticket" in response.url or "Obrigado" in response.text:
        print("✅ Ticket enviado com sucesso.")
    else:
        print("❌ Falha ao enviar o ticket.")
        print(response.text)

# Rota da aplicação
@app.route("/criar_ticket", methods=["GET"])
def criar_ticket_route():
    login()
    criar_ticket()
    return "✅ Ticket Criado com Sucesso!"

# Execução
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

