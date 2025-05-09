from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

LOGIN_URL = "https://widecommerce.freshdesk.com/support/login"
TICKET_URL = "https://widecommerce.freshdesk.com/support/tickets/new"
SUBMIT_URL = "https://widecommerce.freshdesk.com/support/tickets"

# Credenciais fixas
EMAIL = os.getenv("FRESHDESK_EMAIL")
SENHA = os.getenv("FRESHDESK_PASSWORD")


def login(session):
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
    return "logout" in r.text or "Novo ticket" in r.text

def criar_ticket(ticket_email, ticket_subject, ticket_priority, ticket_description):
    session = requests.Session()
    if not login(session):
        return {"status": "erro", "mensagem": "Login falhou"}

    r = session.get(TICKET_URL)
    soup = BeautifulSoup(r.text, 'html.parser')
    token = soup.find("input", {"name": "authenticity_token"})['value']

    payload = {
        "utf8": "✓",
        "authenticity_token": token,
        "helpdesk_ticket[email]": ticket_email,
        "helpdesk_ticket[subject]": ticket_subject,
        "helpdesk_ticket[priority]": ticket_priority,
        "helpdesk_ticket[ticket_body_attributes][description_html]": ticket_description
    }

    response = session.post(SUBMIT_URL, data=payload, allow_redirects=True)

    ticket_id = None
    if "tickets" in response.url:
        parts = response.url.rstrip('/').split('/')
        if parts[-1].isdigit():
            ticket_id = parts[-1]

    return {
        "status": "sucesso" if ticket_id else "erro",
        "ticket_id": ticket_id,
        "url": response.url
    }

@app.route("/criar_ticket", methods=["GET"])
def api_criar_ticket():
    email = request.args.get("email")
    subject = request.args.get("subject")
    priority = request.args.get("priority", "1")
    description = request.args.get("description", "")

    if not all([email, subject]):
        return jsonify({"erro": "Parâmetros obrigatórios: email, subject"})

    resultado = criar_ticket(email, subject, priority, description)
    return jsonify(resultado)

if __name__ == "__main__":
    app.run()
