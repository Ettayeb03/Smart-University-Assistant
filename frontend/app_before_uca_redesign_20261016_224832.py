from frontend.admin_pages import render_admin_pages
import os
import requests
import streamlit as st
from pathlib import Path

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT = 180
LOGO_PATH = Path(__file__).parent / "assets" / "uca_logo.png"

st.set_page_config(
    page_title="UCA | Assistant universitaire",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --uca-blue: #123b65;
    --uca-blue-dark: #0b2744;
    --uca-accent: #2878b5;
    --uca-bg: #f5f7fb;
    --uca-text: #172b42;
    --uca-muted: #68788d;
    --uca-border: #e2e8f0;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: var(--uca-bg);
    color: var(--uca-text);
}

header[data-testid="stHeader"] {
    background: rgba(245,247,251,.92);
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 6rem;
}

section[data-testid="stSidebar"] {
    background: #fff;
    border-right: 1px solid var(--uca-border);
}

section[data-testid="stSidebar"] .block-container {
    padding: 1.2rem 1rem;
}

h1, h2, h3 {
    color: var(--uca-blue-dark);
    letter-spacing: -0.035em;
}

.uca-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0 20px;
}

.uca-brand-title {
    font-size: 16px;
    font-weight: 800;
    color: var(--uca-blue-dark);
    line-height: 1.35;
}

.uca-brand-subtitle {
    color: var(--uca-muted);
    font-size: 11px;
    margin-top: 4px;
}

.uca-eyebrow {
    color: var(--uca-accent);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .13em;
    font-size: 11px;
}

.uca-hero {
    background: linear-gradient(125deg, #102f50 0%, #174f7e 68%, #2878b5 100%);
    color: white;
    padding: 34px 36px;
    border-radius: 22px;
    margin: 8px 0 26px;
    box-shadow: 0 14px 35px rgba(18,59,101,.13);
}

.uca-hero h1 {
    color: white !important;
    font-size: clamp(27px, 3.2vw, 39px);
    font-weight: 800;
    line-height: 1.2;
    margin: 12px 0;
}

.uca-hero p {
    color: #e4effa;
    font-size: 14px;
    line-height: 1.8;
    max-width: 680px;
}

.uca-pill {
    display: inline-block;
    padding: 6px 10px;
    border: 1px solid rgba(255,255,255,.28);
    border-radius: 100px;
    font-size: 11px;
    font-weight: 600;
    color: white;
}

.uca-section-label {
    color: var(--uca-muted);
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin: 12px 0 8px;
}

.uca-card {
    background: white;
    border: 1px solid var(--uca-border);
    border-radius: 16px;
    padding: 20px;
    min-height: 130px;
    box-shadow: 0 4px 15px rgba(21,48,78,.025);
}

.uca-card-title {
    color: var(--uca-blue-dark);
    font-size: 15px;
    font-weight: 700;
    margin: 8px 0;
}

.uca-card-text {
    color: var(--uca-muted);
    font-size: 12px;
    line-height: 1.65;
}

.uca-login-card {
    background: white;
    border: 1px solid var(--uca-border);
    border-radius: 22px;
    padding: 30px;
    box-shadow: 0 15px 45px rgba(21,48,78,.06);
}

div.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    min-height: 42px;
    transition: all .15s ease;
}

div.stButton > button[kind="primary"] {
    background: var(--uca-blue);
    border: 1px solid var(--uca-blue);
}

div.stButton > button[kind="primary"]:hover {
    background: var(--uca-accent);
    border-color: var(--uca-accent);
}

div[data-testid="stChatMessage"] {
    background: white;
    border: 1px solid var(--uca-border);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 12px;
}

div[data-testid="stChatInput"] {
    border-color: #cbd8e6;
    border-radius: 15px;
}

div[data-testid="stExpander"] {
    background: white;
    border: 1px solid var(--uca-border);
    border-radius: 12px;
}

div[data-testid="stTextInput"] input {
    border-radius: 10px;
}

.uca-footer {
    border-top: 1px solid var(--uca-border);
    margin-top: 36px;
    padding-top: 15px;
    color: var(--uca-muted);
    font-size: 11px;
    text-align: center;
}

.uca-status {
    color: #27744a;
    background: #eaf7ef;
    padding: 5px 9px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
}

@media (max-width: 700px) {
    .block-container { padding: 1rem 1rem 5rem; }
    .uca-hero { padding: 24px 20px; }
}
</style>
""", unsafe_allow_html=True)


# ---------- Session ----------
defaults = {
    "token": None,
    "conversations": [],
    "conversation_id": None,
    "messages": [],
    "notice": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- API ----------
def api_request(method, path, **kwargs):
    headers = dict(kwargs.pop("headers", {}))
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"

    try:
        response = requests.request(
            method,
            f"{API_URL}{path}",
            headers=headers,
            timeout=TIMEOUT,
            **kwargs,
        )
    except requests.RequestException:
        st.error(
            "Impossible de joindre le serveur. Vérifie que FastAPI fonctionne "
            "sur http://127.0.0.1:8000."
        )
        return None

    if response.status_code == 401:
        st.session_state.token = None
        st.session_state.conversations = []
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.error("Session expirée. Connecte-toi à nouveau.")
        st.rerun()

    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        st.error(f"Erreur API ({response.status_code}) : {detail}")
        return None

    if response.status_code == 204 or not response.content:
        return {}

    return response.json()


def load_conversations():
    result = api_request("GET", "/chat/conversations")
    if result is not None:
        st.session_state.conversations = result


def load_messages(conversation_id):
    result = api_request(
        "GET", f"/chat/conversations/{conversation_id}/messages"
    )
    if result is not None:
        st.session_state.messages = result
        st.session_state.conversation_id = conversation_id


def new_conversation():
    result = api_request(
        "POST",
        "/chat/conversations",
        json={"title": "Nouvelle conversation"},
    )
    if result:
        st.session_state.conversation_id = result["id"]
        st.session_state.messages = []
        st.session_state.notice = "Nouvelle conversation créée."
        load_conversations()
        st.rerun()


def rename_conversation(conversation_id, title):
    result = api_request(
        "PATCH",
        f"/chat/conversations/{conversation_id}",
        json={"title": title},
    )
    if result:
        st.session_state.notice = "Conversation renommée."
        load_conversations()
        st.rerun()


def delete_conversation(conversation_id):
    result = api_request(
        "DELETE", f"/chat/conversations/{conversation_id}"
    )
    if result is not None:
        if st.session_state.conversation_id == conversation_id:
            st.session_state.conversation_id = None
            st.session_state.messages = []
        st.session_state.notice = "Conversation supprimée."
        load_conversations()
        st.rerun()


def send_question(question):
    payload = {"question": question, "top_k": 4}
    if st.session_state.conversation_id is not None:
        payload["conversation_id"] = st.session_state.conversation_id

    result = api_request("POST", "/chat/ask", json=payload)
    if result:
        st.session_state.conversation_id = result["conversation_id"]
        load_messages(result["conversation_id"])
        load_conversations()


def show_logo(width=180):
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=width)
    else:
        st.markdown("## 🎓 UCA")


# ---------- Login ----------
if not st.session_state.token:
    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.write("")
        st.write("")
        show_logo(190)
        st.markdown(
            """
            <div class="uca-eyebrow">Université Cadi Ayyad</div>
            <div style="font-size:36px;font-weight:800;line-height:1.2;
                        color:#0b2744;margin:14px 0 18px">
                Votre université,<br>en toute simplicité.
            </div>
            <div style="font-size:15px;color:#68788d;line-height:1.9">
                Accédez aux informations universitaires et interrogez
                vos ressources documentaires grâce à un assistant
                intelligent basé sur l'intelligence artificielle.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown(
            """
            <div class="uca-card">
              <div class="uca-card-title">✦ Recherche intelligente</div>
              <div class="uca-card-text">
                Posez vos questions en langage naturel et obtenez des réponses
                appuyées sur les documents disponibles.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.write("")
        st.write("")
        st.markdown('<div class="uca-login-card">', unsafe_allow_html=True)
        st.markdown("### Bienvenue")
        st.markdown(
            "<p style='color:#68788d;font-size:13px'>"
            "Connectez-vous pour accéder à votre assistant universitaire.</p>",
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            email = st.text_input("Adresse e-mail", placeholder="nom@exemple.ma")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button(
                "Se connecter  →", type="primary", use_container_width=True
            )

        if submitted:
            if not email.strip() or not password:
                st.warning("Renseigne ton adresse e-mail et ton mot de passe.")
            else:
                result = api_request(
                    "POST",
                    "/auth/login",
                    json={"email": email.strip(), "password": password},
                )
                if result and result.get("access_token"):
                    st.session_state.token = result["access_token"]
                    st.session_state.conversations = []
                    st.session_state.conversation_id = None
                    st.session_state.messages = []
                    st.rerun()

        st.markdown(
            "<div style='color:#8a97a8;font-size:11px;margin-top:18px'>"
            "Accès réservé aux utilisateurs autorisés.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="uca-footer">Smart University Assistant · '
        'Université Cadi Ayyad</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ---------- Authenticated area ----------
user = api_request("GET", "/auth/me")
if user is None:
    st.stop()

if render_admin_pages(api_request, user):
    st.stop()
if not st.session_state.conversations:
    load_conversations()

with st.sidebar:
    show_logo(155)
    st.markdown(
        '<div class="uca-brand"><div>'
        '<div class="uca-brand-title">Smart University<br>Assistant</div>'
        '<div class="uca-brand-subtitle">Votre espace intelligent</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="uca-section-label">ESPACE PERSONNEL</div>',
                unsafe_allow_html=True)

    if st.button("＋  Nouvelle conversation", type="primary",
                 use_container_width=True):
        new_conversation()

    if st.button("↻  Actualiser", use_container_width=True):
        load_conversations()
        st.rerun()

    st.markdown('<div class="uca-section-label">HISTORIQUE</div>',
                unsafe_allow_html=True)

    for conversation in st.session_state.conversations:
        cid = conversation["id"]
        title = conversation.get("title") or "Nouvelle conversation"

        with st.container(border=True):
            if st.button(
                title,
                key=f"open_{cid}",
                use_container_width=True,
                type="primary"
                if cid == st.session_state.conversation_id
                else "secondary",
            ):
                load_messages(cid)
                st.rerun()

            with st.expander("Gérer la conversation"):
                with st.form(f"rename_form_{cid}"):
                    new_title = st.text_input(
                        "Nom de la conversation",
                        value=title,
                        max_chars=200,
                        key=f"title_{cid}",
                    )
                    rename_submitted = st.form_submit_button("Renommer")

                if rename_submitted:
                    if new_title.strip():
                        rename_conversation(cid, new_title.strip())
                    else:
                        st.warning("Le nom ne peut pas être vide.")

                delete_key = f"confirm_delete_{cid}"
                if st.button("Supprimer", key=f"delete_{cid}",
                             use_container_width=True):
                    st.session_state[delete_key] = True

                if st.session_state.get(delete_key, False):
                    st.warning("La suppression est définitive.")
                    col1, col2 = st.columns(2)
                    if col1.button("Confirmer", key=f"confirm_{cid}"):
                        st.session_state[delete_key] = False
                        delete_conversation(cid)
                    if col2.button("Annuler", key=f"cancel_{cid}"):
                        st.session_state[delete_key] = False
                        st.rerun()

    st.divider()
    st.caption(user.get("email", "Utilisateur connecté"))
    if st.button("Se déconnecter", use_container_width=True):
        for key in ("token", "conversations", "conversation_id", "messages"):
            st.session_state[key] = (
                None if key in ("token", "conversation_id") else []
            )
        st.rerun()


# ---------- Main page ----------
header_left, header_right = st.columns([0.78, 0.22])
with header_left:
    st.markdown(
        '<div class="uca-eyebrow">UNIVERSITÉ CADI AYYAD</div>'
        '<h2 style="margin:5px 0 0">Assistant universitaire</h2>',
        unsafe_allow_html=True,
    )
with header_right:
    st.markdown(
        '<div style="text-align:right;padding-top:12px">'
        '<span class="uca-status">● Connecté</span></div>',
        unsafe_allow_html=True,
    )

st.divider()

if st.session_state.notice:
    st.toast(st.session_state.notice)
    st.session_state.notice = None

if st.session_state.conversation_id is None:
    st.markdown(
        """
        <div class="uca-hero">
          <span class="uca-pill">✦ Assistant intelligent</span>
          <h1>Bonjour, comment<br>puis-je vous aider ?</h1>
          <p>
            Posez vos questions sur l'université. L'assistant recherche
            les informations dans les documents disponibles et présente
            les sources utilisées pour répondre.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Commencez votre recherche")
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(
            '<div class="uca-card"><div style="font-size:23px">📚</div>'
            '<div class="uca-card-title">Informations universitaires</div>'
            '<div class="uca-card-text">Découvrez les établissements et '
            'les informations présentes dans la base documentaire.</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="uca-card"><div style="font-size:23px">🔎</div>'
            '<div class="uca-card-title">Recherche documentaire</div>'
            '<div class="uca-card-text">Retrouvez des informations '
            'pertinentes à partir de vos questions.</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            '<div class="uca-card"><div style="font-size:23px">💬</div>'
            '<div class="uca-card-title">Dialogue contextuel</div>'
            '<div class="uca-card-text">Posez des questions complémentaires '
            'dans une même conversation.</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    if st.button("＋  Démarrer une conversation",
                 type="primary", use_container_width=False):
        new_conversation()
else:
    active = next(
        (c for c in st.session_state.conversations
         if c["id"] == st.session_state.conversation_id),
        None,
    )
    st.markdown(
        f"#### {active.get('title', 'Conversation') if active else 'Conversation'}"
    )

    for message in st.session_state.messages:
        role = "assistant" if message["role"] == "assistant" else "user"
        with st.chat_message(role):
            st.markdown(message["content"])
            sources = message.get("sources") or []
            if role == "assistant" and sources:
                with st.expander(f"Sources documentaires ({len(sources)})"):
                    for source in sources:
                        st.markdown(
                            f"- **{source.get('source', 'Source inconnue')}**  \n"
                            f"Passage : {source.get('chunk_index', '-')} · "
                            f"Distance : {source.get('distance', '-')}"
                        )

    question = st.chat_input("Écrivez votre question ici…")
    if question:
        with st.chat_message("user"):
            st.markdown(question)
        with st.spinner("Analyse des documents et préparation de la réponse…"):
            send_question(question)
        st.rerun()

st.markdown(
    '<div class="uca-footer">Smart University Assistant · '
    'Université Cadi Ayyad · Propulsé par l’IA</div>',
    unsafe_allow_html=True,
)


