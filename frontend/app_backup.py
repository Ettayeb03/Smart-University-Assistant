import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT = 180

st.set_page_config(
    page_title="Smart University Assistant",
    page_icon="🎓",
    layout="wide",
)

if "token" not in st.session_state:
    st.session_state.token = None
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "notice" not in st.session_state:
    st.session_state.notice = None


def api_request(method, path, **kwargs):
    headers = kwargs.pop("headers", {})
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
    except requests.RequestException as exc:
        st.error(f"Impossible de joindre l'API : {exc}")
        return None

    if response.status_code == 401:
        st.session_state.token = None
        st.error("Session expirée ou identifiants invalides. Reconnecte-toi.")
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
        "GET",
        f"/chat/conversations/{conversation_id}/messages",
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
        st.session_state.notice = "Conversation créée."
        load_conversations()
        st.rerun()


def rename_conversation(conversation_id, title):
    result = api_request(
        "PATCH",
        f"/chat/conversations/{conversation_id}",
        json={"title": title},
    )
    if result:
        st.session_state.notice = "Nom de conversation modifié."
        load_conversations()
        st.rerun()


def delete_conversation(conversation_id):
    result = api_request(
        "DELETE",
        f"/chat/conversations/{conversation_id}",
    )
    if result is not None:
        if st.session_state.conversation_id == conversation_id:
            st.session_state.conversation_id = None
            st.session_state.messages = []
        st.session_state.notice = "Conversation supprimée."
        load_conversations()
        st.rerun()


def send_question(question):
    payload = {
        "question": question,
        "top_k": 4,
    }
    if st.session_state.conversation_id is not None:
        payload["conversation_id"] = st.session_state.conversation_id

    result = api_request("POST", "/chat/ask", json=payload)
    if result:
        st.session_state.conversation_id = result["conversation_id"]
        load_messages(result["conversation_id"])
        load_conversations()


st.title("🎓 Smart University Assistant")
st.caption("Assistant intelligent pour les informations universitaires")

if st.session_state.notice:
    st.toast(st.session_state.notice)
    st.session_state.notice = None

# Connexion
if not st.session_state.token:
    st.subheader("Connexion")
    with st.form("login_form"):
        email = st.text_input("Adresse e-mail")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter", type="primary")

    if submitted:
        result = api_request(
            "POST",
            "/auth/login",
            json={"email": email, "password": password},
            headers={},
        )
        if result and result.get("access_token"):
            st.session_state.token = result["access_token"]
            st.session_state.conversations = []
            st.session_state.conversation_id = None
            st.session_state.messages = []
            st.rerun()
    st.stop()

# Vérifier le jeton et récupérer l'utilisateur courant.
user = api_request("GET", "/auth/me")
if user is None:
    st.stop()

with st.sidebar:
    st.header("Conversations")
    st.caption(user.get("email", "Utilisateur connecté"))

    if st.button("＋ Nouvelle conversation", use_container_width=True):
        new_conversation()

    if st.button("↻ Actualiser", use_container_width=True):
        load_conversations()
        st.rerun()

    if not st.session_state.conversations:
        load_conversations()

    for conversation in st.session_state.conversations:
        cid = conversation["id"]
        title = conversation.get("title") or "Nouvelle conversation"

        with st.container(border=True):
            if st.button(
                title,
                key=f"open_{cid}",
                use_container_width=True,
                type="primary" if cid == st.session_state.conversation_id else "secondary",
            ):
                load_messages(cid)
                st.rerun()

            with st.expander("Gérer"):
                with st.form(f"rename_form_{cid}"):
                    new_title = st.text_input(
                        "Nouveau nom",
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

                if st.button(
                    "🗑️ Supprimer cette conversation",
                    key=f"delete_{cid}",
                    use_container_width=True,
                ):
                    st.session_state[f"confirm_delete_{cid}"] = True

                if st.session_state.get(f"confirm_delete_{cid}", False):
                    st.warning("Cette suppression est définitive.")
                    col1, col2 = st.columns(2)
                    if col1.button("Confirmer", key=f"confirm_{cid}"):
                        st.session_state[f"confirm_delete_{cid}"] = False
                        delete_conversation(cid)
                    if col2.button("Annuler", key=f"cancel_{cid}"):
                        st.session_state[f"confirm_delete_{cid}"] = False
                        st.rerun()

    st.divider()
    if st.button("Se déconnecter", use_container_width=True):
        st.session_state.token = None
        st.session_state.conversations = []
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()

# Affichage du chat
if st.session_state.conversation_id is None:
    st.info("Choisis une conversation ou crée-en une nouvelle.")
else:
    for message in st.session_state.messages:
        role = "assistant" if message["role"] == "assistant" else "user"
        with st.chat_message(role):
            st.markdown(message["content"])
            sources = message.get("sources") or []
            if role == "assistant" and sources:
                with st.expander(f"Sources ({len(sources)})"):
                    for source in sources:
                        st.write(
                            f"- {source.get('source', 'Source inconnue')} "
                            f"(passage {source.get('chunk_index', '-')}, "
                            f"distance {source.get('distance', '-')})"
                        )

    question = st.chat_input("Pose ta question sur l'université…")
    if question:
        with st.chat_message("user"):
            st.markdown(question)

        with st.spinner("Recherche documentaire et génération de la réponse…"):
            send_question(question)

        st.rerun()
