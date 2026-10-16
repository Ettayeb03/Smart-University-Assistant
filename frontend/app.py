
import os
import base64
from pathlib import Path

import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

REQUEST_TIMEOUT = 30

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "logo_uca.png"

st.set_page_config(
    page_title="Smart University Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN GLOBAL
# ============================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #f7f9fc;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e7ebf2;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.3rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 0 22px 0;
    }

    .brand-icon {
        background: linear-gradient(135deg, #2563eb, #4f46e5);
        color: white;
        border-radius: 13px;
        width: 46px;
        height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 23px;
        flex-shrink: 0;
    }

    .brand-title {
        font-size: 17px;
        font-weight: 800;
        color: #172554;
        line-height: 1.4;
    }

    .brand-subtitle {
        color: #718096;
        font-size: 11px;
        margin-top: 3px;
    }

    .topbar {
        padding: 12px 0;
        border-bottom: 1px solid #e7ebf2;
        margin-bottom: 24px;
        color: #64748b;
        font-size: 13px;
    }

    .hero {
        text-align: center;
        padding: 35px 10px 25px 10px;
    }

    .hero h1 {
        color: #172554;
        font-size: clamp(26px, 3vw, 36px);
        font-weight: 800;
        letter-spacing: -1px;
    }

    .hero p {
        color: #64748b;
        font-size: 15px;
        line-height: 1.8;
    }

    .feature-card {
        background: #ffffff;
        border: 1px solid #e5eaf3;
        border-radius: 16px;
        padding: 18px;
        min-height: 125px;
        margin-bottom: 10px;
    }

    .feature-card h4 {
        color: #1e293b;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .feature-card p {
        color: #64748b;
        font-size: 12px;
        line-height: 1.7;
        margin-bottom: 0;
    }

    .section-title {
        color: #172554;
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .section-description {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 22px;
    }

    .small-muted {
        color: #64748b;
        font-size: 12px;
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        min-height: 40px;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        border-color: #93b4f8;
    }

    [data-testid="stChatMessage"] {
        border: 1px solid #edf0f5;
        border-radius: 15px;
        padding: 14px;
        background: #ffffff;
    }

    [data-testid="stChatInput"] {
        border-radius: 14px;
    }

    [data-testid="stForm"] {
        border: none;
    }

    footer {
        visibility: hidden;
    }

    /* ================================================
       LOGIN PAGE
       ================================================ */

    [data-testid="stAppViewContainer"] {
        min-height: 100vh;
    }

    .login-logo {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto 12px auto;
    }

    .login-title {
        color: #172554;
        font-size: clamp(23px, 2.5vw, 31px);
        font-weight: 800;
        line-height: 1.3;
        letter-spacing: -0.8px;
        text-align: center;
        margin: 8px 0 10px 0;
    }

    .login-subtitle {
        color: #64748b;
        font-size: 13px;
        line-height: 1.7;
        text-align: center;
        margin: 0 auto 24px auto;
        max-width: 380px;
    }

    .login-footer {
        color: #94a3b8;
        font-size: 11px;
        line-height: 1.8;
        text-align: center;
        margin-top: 18px;
    }

    /* Limiter la largeur du formulaire */
    .st-key-login-card {
        width: 100%;
        max-width: 440px;
        margin-left: auto;
        margin-right: auto;
    }

    .st-key-login-card [data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        box-shadow: 0 12px 36px rgba(15, 23, 42, 0.06);
    }

    .st-key-login-card input {
        border-radius: 10px;
    }

    .st-key-login-card button {
        border-radius: 10px;
    }

    @media (max-width: 768px) {
        .login-title {
            font-size: 24px;
        }

        .login-subtitle {
            font-size: 12px;
        }

        .section-title {
            font-size: 22px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "token": None,
    "authenticated": False,
    "user": None,
    "page": "chat",
    "conversations": [],
    "conversations_loaded": False,
    "current_conversation_id": None,
    "messages": [],
    "login_error": None,
    "api_error": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# API HELPERS
# ============================================================

def api_request(method, endpoint, **kwargs):
    """Envoie une requête HTTP à l'API FastAPI."""

    headers = dict(kwargs.pop("headers", {}))

    token = st.session_state.get("token")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.request(
            method=method,
            url=f"{API_URL}{endpoint}",
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )

        if response.status_code == 204:
            return None

        if response.status_code == 401:
            return {
                "_error": "401",
                "detail": "Session expirée ou accès refusé.",
            }

        if not response.ok:
            try:
                body = response.json()
                detail = body.get("detail", response.text)
            except (ValueError, AttributeError):
                detail = response.text

            return {
                "_error": str(response.status_code),
                "detail": str(detail)[:500],
            }

        if not response.content:
            return None

        return response.json()

    except requests.exceptions.ConnectionError:
        return {
            "_error": "CONNECTION",
            "detail": (
                "Backend inaccessible. Vérifie que FastAPI "
                "est lancé sur http://127.0.0.1:8000."
            ),
        }

    except requests.exceptions.Timeout:
        return {
            "_error": "TIMEOUT",
            "detail": "Le serveur ne répond pas dans le délai prévu.",
        }

    except requests.exceptions.RequestException as exc:
        return {
            "_error": "REQUEST",
            "detail": str(exc),
        }


def is_api_error(data):
    return isinstance(data, dict) and "_error" in data


# ============================================================
# AUTHENTIFICATION
# ============================================================

def authenticate(email, password):
    """Authentifie l'utilisateur auprès du backend."""

    email = email.strip()

    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={
                "email": email,
                "password": password,
            },
            timeout=15,
        )

        # Compatibilité avec une authentification OAuth2.
        if response.status_code in (404, 405, 422):
            response = requests.post(
                f"{API_URL}/auth/token",
                data={
                    "username": email,
                    "password": password,
                },
                timeout=15,
            )

        if response.status_code == 200:
            data = response.json()

            token = (
                data.get("access_token")
                or data.get("token")
            )

            if not token:
                return (
                    False,
                    None,
                    "La réponse de l'API ne contient pas de token.",
                )

            return True, token, None

        if response.status_code in (401, 403):
            return (
                False,
                None,
                "E-mail ou mot de passe incorrect.",
            )

        try:
            detail = response.json().get(
                "detail",
                response.text,
            )
        except (ValueError, AttributeError):
            detail = response.text

        return (
            False,
            None,
            f"Erreur API {response.status_code} : {str(detail)[:300]}",
        )

    except requests.exceptions.ConnectionError:
        return (
            False,
            None,
            "Backend inaccessible. Lance d'abord le serveur FastAPI.",
        )

    except requests.exceptions.Timeout:
        return False, None, "Le serveur ne répond pas."

    except requests.exceptions.RequestException as exc:
        return False, None, f"Erreur de connexion : {exc}"


def logout():
    """Réinitialise la session locale."""

    for key, value in DEFAULTS.items():
        st.session_state[key] = value

    st.rerun()


def render_login_logo():
    """Affiche le logo UCA centré."""

    if not LOGO_PATH.is_file():
        st.warning("Logo introuvable : frontend/assets/logo_uca.png")
        return

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        st.image(
            str(LOGO_PATH),
            width=115,
        )

def login_page():
    """Page de connexion centrée avec une largeur contrôlée."""

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    left, center, right = st.columns([1, 1.5, 1])

    with center:
        render_login_logo()

        st.markdown(
            """
            <div class="login-title">
                Smart University Assistant
            </div>

            <div class="login-subtitle">
                Votre espace intelligent pour rechercher,
                comprendre et exploiter les connaissances
                universitaires.
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(
            border=True,
            key="login-card",
        ):
            st.markdown("### Bienvenue")
            st.caption(
                "Connectez-vous pour accéder à votre espace."
            )

            with st.form("login_form"):
                email = st.text_input(
                    "Adresse e-mail",
                    placeholder="nom@universite.ma",
                    autocomplete="email",
                )

                password = st.text_input(
                    "Mot de passe",
                    type="password",
                    placeholder="Votre mot de passe",
                    autocomplete="current-password",
                )

                submitted = st.form_submit_button(
                    "Se connecter",
                    type="primary",
                    use_container_width=True,
                )

            if st.session_state.get("login_error"):
                st.error(st.session_state["login_error"])

            if submitted:
                if not email.strip() or not password:
                    st.session_state["login_error"] = (
                        "Veuillez saisir votre e-mail "
                        "et votre mot de passe."
                    )
                    st.rerun()

                with st.spinner("Vérification des identifiants..."):
                    success, token, error = authenticate(
                        email,
                        password,
                    )

                if not success:
                    st.session_state["login_error"] = error
                    st.rerun()

                st.session_state["token"] = token
                st.session_state["authenticated"] = True
                st.session_state["login_error"] = None

                profile = api_request("GET", "/auth/me")

                if is_api_error(profile):
                    st.session_state["token"] = None
                    st.session_state["authenticated"] = False
                    st.session_state["user"] = None
                    st.session_state["login_error"] = (
                        "Connexion établie, mais impossible "
                        "de charger le profil : "
                        + profile["detail"]
                    )
                    st.rerun()

                st.session_state["user"] = profile
                st.session_state["page"] = "chat"
                st.session_state["api_error"] = None
                st.session_state["conversations_loaded"] = False
                st.rerun()

        st.markdown(
            """
            <div class="login-footer">
                Accès sécurisé · Smart University Assistant<br>
                Université Cadi Ayyad
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# UTILISATEUR ET RÔLE
# ============================================================

def user_role():
    user = st.session_state.get("user") or {}

    role = user.get(
        "role",
        user.get("user_role", "user"),
    )

    if isinstance(role, dict):
        role = role.get("name", "user")

    return str(role).lower()


def user_display_name():
    user = st.session_state.get("user") or {}

    return (
        user.get("full_name")
        or user.get("name")
        or user.get("email")
        or user.get("username")
        or "Utilisateur"
    )


# ============================================================
# CONVERSATIONS
# ============================================================

def extract_list(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in (
            "items",
            "results",
            "conversations",
            "messages",
        ):
            if isinstance(data.get(key), list):
                return data[key]

    return []


def conversation_id_of(conversation):
    if not isinstance(conversation, dict):
        return None

    return (
        conversation.get("id")
        or conversation.get("conversation_id")
    )


def load_conversations():
    data = api_request(
        "GET",
        "/chat/conversations",
    )

    if is_api_error(data):
        st.session_state["api_error"] = data["detail"]
        return

    st.session_state["conversations"] = extract_list(data)
    st.session_state["conversations_loaded"] = True


def load_messages(conversation_id):
    data = api_request(
        "GET",
        f"/chat/conversations/{conversation_id}/messages",
    )

    if is_api_error(data):
        st.session_state["api_error"] = data["detail"]
        st.session_state["messages"] = []
        return

    st.session_state["messages"] = extract_list(data)


def create_conversation():
    data = api_request(
        "POST",
        "/chat/conversations",
        json={"title": "Nouvelle conversation"},
    )

    if is_api_error(data):
        st.session_state["api_error"] = data["detail"]
        return

    if isinstance(data, dict):
        conversation_id = conversation_id_of(data)

        if conversation_id is not None:
            st.session_state["current_conversation_id"] = (
                conversation_id
            )
            st.session_state["messages"] = []
            st.session_state["page"] = "chat"
            st.session_state["api_error"] = None
            load_conversations()
            st.rerun()

    st.session_state["api_error"] = (
        "La création a répondu sans identifiant de conversation."
    )


def select_conversation(conversation_id):
    st.session_state["current_conversation_id"] = conversation_id
    st.session_state["api_error"] = None

    load_messages(conversation_id)

    st.session_state["page"] = "chat"


def rename_conversation(conversation):
    conversation_id = conversation_id_of(conversation)

    if conversation_id is None:
        st.warning("Identifiant de conversation introuvable.")
        return

    current_title = (
        conversation.get("title")
        or conversation.get("name")
        or "Conversation"
    )

    title = st.text_input(
        "Nouveau titre",
        value=current_title,
        key=f"rename_{conversation_id}",
    )

    if st.button(
        "Enregistrer le titre",
        key=f"save_{conversation_id}",
    ):
        if not title.strip():
            st.warning("Le titre ne peut pas être vide.")
            return

        result = api_request(
            "PATCH",
            f"/chat/conversations/{conversation_id}",
            json={"title": title.strip()},
        )

        if is_api_error(result):
            st.error(result["detail"])
        else:
            st.session_state["api_error"] = None
            load_conversations()
            st.rerun()


def delete_conversation(conversation_id):
    result = api_request(
        "DELETE",
        f"/chat/conversations/{conversation_id}",
    )

    if is_api_error(result):
        st.session_state["api_error"] = result["detail"]
        return

    if (
        st.session_state["current_conversation_id"]
        == conversation_id
    ):
        st.session_state["current_conversation_id"] = None
        st.session_state["messages"] = []

    st.session_state.pop(
        f"confirm_delete_{conversation_id}",
        None,
    )

    st.session_state["api_error"] = None
    load_conversations()
    st.rerun()


# ============================================================
# CHAT
# ============================================================

def message_role(message):
    role = (
        message.get("role")
        or message.get("sender")
        or message.get("message_type")
        or "assistant"
    )

    role = str(role).lower()

    if role in ("user", "human", "utilisateur"):
        return "user"

    return "assistant"


def message_content(message):
    return (
        message.get("content")
        or message.get("message")
        or message.get("text")
        or message.get("answer")
        or ""
    )


def display_sources(sources):
    if not sources:
        return

    with st.expander("📚 Sources utilisées"):
        for index, source in enumerate(sources, start=1):
            if isinstance(source, str):
                st.markdown(f"**Source {index}** — {source}")
                continue

            if not isinstance(source, dict):
                continue

            name = (
                source.get("filename")
                or source.get("document_name")
                or source.get("title")
                or source.get("name")
                or f"Document {index}"
            )

            content = (
                source.get("content")
                or source.get("text")
                or source.get("excerpt")
                or ""
            )

            st.markdown(f"**{index}. {name}**")

            if content:
                st.caption(str(content)[:1200])


def ask_question(question):
    conversation_id = st.session_state.get(
        "current_conversation_id"
    )

    payload = {
        "question": question,
        "top_k": 4,
    }

    if conversation_id is not None:
        payload["conversation_id"] = conversation_id

    result = api_request(
        "POST",
        "/chat/ask",
        json=payload,
    )

    if is_api_error(result):
        st.session_state["api_error"] = result["detail"]
        return

    if not isinstance(result, dict):
        st.session_state["api_error"] = (
            "Le serveur a renvoyé une réponse inattendue."
        )
        return

    conversation = result.get("conversation")

    returned_id = result.get("conversation_id")

    if returned_id is None and isinstance(conversation, dict):
        returned_id = conversation.get("id")

    if returned_id is not None:
        st.session_state["current_conversation_id"] = returned_id

    answer = (
        result.get("answer")
        or result.get("response")
        or result.get("content")
        or "Aucune réponse n'a été retournée."
    )

    st.session_state["messages"].append(
        {
            "role": "user",
            "content": question,
        }
    )

    st.session_state["messages"].append(
        {
            "role": "assistant",
            "content": answer,
            "sources": result.get("sources", []),
        }
    )

    load_conversations()


def render_chat():
    st.markdown(
        '<div class="section-title">'
        'Assistant universitaire'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Posez vos questions et explorez les ressources universitaires.'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.get("api_error"):
        st.error(st.session_state["api_error"])

        if st.button("Fermer le message"):
            st.session_state["api_error"] = None
            st.rerun()

    if not st.session_state["messages"]:
        st.markdown(
            """
            <div class="hero">
                <div style="font-size:38px">✨</div>
                <h1>Comment puis-je vous aider ?</h1>
                <p>
                    Interrogez les documents et les connaissances
                    de votre université en langage naturel.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                """
                <div class="feature-card">
                    <h4>📖 Comprendre un cours</h4>
                    <p>
                        Obtenez une explication claire
                        d'un concept universitaire.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                """
                <div class="feature-card">
                    <h4>🔎 Rechercher un document</h4>
                    <p>
                        Retrouvez des informations
                        dans les ressources disponibles.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                """
                <div class="feature-card">
                    <h4>🧠 Synthétiser</h4>
                    <p>
                        Résumez les informations utiles
                        à vos études et vos recherches.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    for message in st.session_state["messages"]:
        role = message_role(message)

        avatar = "👤" if role == "user" else "🎓"

        with st.chat_message(role, avatar=avatar):
            st.markdown(message_content(message))

            if role == "assistant":
                display_sources(message.get("sources", []))

    question = st.chat_input(
        "Posez votre question à l'assistant..."
    )

    if question and question.strip():
        st.session_state["api_error"] = None

        with st.spinner(
            "Recherche et préparation de la réponse..."
        ):
            ask_question(question.strip())

        st.rerun()


# ============================================================
# ADMINISTRATION
# ============================================================

def render_admin():
    st.markdown(
        '<div class="section-title">Administration</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Gestion et supervision de la plateforme.'
        '</div>',
        unsafe_allow_html=True,
    )

    tab_dashboard, tab_users, tab_documents = st.tabs(
        [
            "📊 Tableau de bord",
            "👥 Utilisateurs",
            "📄 Documents",
        ]
    )

    with tab_dashboard:
        data = api_request("GET", "/admin/dashboard")

        if is_api_error(data):
            st.error(data["detail"])
        elif isinstance(data, dict):
            st.json(data)
        else:
            st.info("Aucune donnée disponible.")

    with tab_users:
        users = api_request("GET", "/admin/users")

        if is_api_error(users):
            st.error(users["detail"])
        else:
            users_list = extract_list(users)

            if users_list:
                st.dataframe(
                    users_list,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("Aucun utilisateur à afficher.")

    with tab_documents:
        documents = api_request("GET", "/documents")

        if is_api_error(documents):
            st.error(documents["detail"])
        else:
            docs_list = extract_list(documents)

            if docs_list:
                st.dataframe(
                    docs_list,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("Aucun document à afficher.")


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar(role):
    with st.sidebar:
        # Logo UCA
        if LOGO_PATH.is_file():
            logo_base64 = base64.b64encode(
                LOGO_PATH.read_bytes()
            ).decode("utf-8")

            logo_html = f"""
                <img
                    src="data:assets/logo_uca.png;base64,{logo_base64}"
                    style="
                        width:46px;
                        height:46px;
                        object-fit:contain;
                        border-radius:10px;
                        background:white;
                        flex-shrink:0;
                    "
                >
            """
        else:
            logo_html = '<div class="brand-icon">🎓</div>'

        st.markdown(
            f"""
            <div class="brand">
                {logo_html}
                <div>
                    <div class="brand-title">Smart Assistant</div>
                    <div class="brand-subtitle">
                        University Knowledge Hub
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(f"**{user_display_name()}**")
        st.caption(f"Rôle : {role}")

        st.divider()

        if st.button(
            "＋ Nouvelle conversation",
            use_container_width=True,
            type="primary",
        ):
            create_conversation()

        if st.button(
            "💬 Assistant",
            use_container_width=True,
        ):
            st.session_state["page"] = "chat"
            st.rerun()

        if role in (
            "admin",
            "administrator",
            "superadmin",
        ):
            if st.button(
                "⚙️ Administration",
                use_container_width=True,
            ):
                st.session_state["page"] = "admin"
                st.rerun()

        st.divider()

        st.markdown("**Historique**")

        if st.button(
            "↻ Actualiser",
            use_container_width=True,
        ):
            load_conversations()
            st.rerun()

        conversations = st.session_state.get(
            "conversations",
            [],
        )

        if not conversations:
            st.caption("Aucune conversation enregistrée.")

        else:
            for conversation in conversations:
                if not isinstance(conversation, dict):
                    continue

                conversation_id = conversation_id_of(
                    conversation
                )

                if conversation_id is None:
                    continue

                title = (
                    conversation.get("title")
                    or conversation.get("name")
                    or "Nouvelle conversation"
                )

                with st.container():
                    if st.button(
                        f"💬 {title}",
                        key=f"conversation_{conversation_id}",
                        use_container_width=True,
                    ):
                        select_conversation(conversation_id)
                        st.rerun()

                    with st.popover("⋯"):
                        rename_conversation(conversation)

                        confirm_key = (
                            f"confirm_delete_{conversation_id}"
                        )

                        if st.button(
                            "🗑️ Supprimer",
                            key=f"delete_{conversation_id}",
                            use_container_width=True,
                        ):
                            st.session_state[confirm_key] = True

                        if st.session_state.get(confirm_key, False):
                            st.warning(
                                "Confirmer la suppression définitive ?"
                            )

                            if st.button(
                                "Confirmer la suppression",
                                key=f"confirm_{conversation_id}",
                                type="primary",
                                use_container_width=True,
                            ):
                                delete_conversation(conversation_id)

        st.divider()

        if st.button(
            "🚪 Déconnexion",
            use_container_width=True,
        ):
            logout()

        st.markdown(
            '<p class="small-muted">'
            'Smart University Assistant'
            '</p>',
            unsafe_allow_html=True,
        )


# ============================================================
# APPLICATION PRINCIPALE
# ============================================================

def main():
    # Écran de connexion
    if not st.session_state.get("authenticated"):
        login_page()
        return

    # Vérifier le profil si nécessaire.
    if not st.session_state.get("user"):
        profile = api_request("GET", "/auth/me")

        if is_api_error(profile):
            st.session_state["token"] = None
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.session_state["login_error"] = (
                "Session invalide. Veuillez vous reconnecter."
            )
            st.rerun()

        st.session_state["user"] = profile

    # Charger l'historique une fois par session, puis le mettre
    # à jour après les opérations sur les conversations.
    if not st.session_state.get("conversations_loaded"):
        load_conversations()

    role = user_role()

    render_sidebar(role)

    current_page = st.session_state.get("page", "chat")

    page_label = (
        "Administration"
        if current_page == "admin"
        else "Assistant"
    )

    st.markdown(
        f'<div class="topbar">'
        f'Espace de travail / {page_label}'
        f'</div>',
        unsafe_allow_html=True,
    )

    if (
        current_page == "admin"
        and role in (
            "admin",
            "administrator",
            "superadmin",
        )
    ):
        render_admin()
    else:
        render_chat()


if __name__ == "__main__":
    main()
