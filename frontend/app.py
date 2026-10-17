
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
import streamlit as st


# ============================================================
# 1. CONFIGURATION
# ============================================================

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = 30
CHAT_TIMEOUT = 120

BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATHS = [
    BASE_DIR / "frontend" / "assets" / "uca_logo.png",
    Path(__file__).resolve().parent / "assets" / "uca_logo.png",
]

st.set_page_config(
    page_title="UCA | Assistant universitaire",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. DESIGN — INTERFACE ÉPURÉE
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --uca-blue: #123b69;
        --uca-dark: #0b2545;
        --uca-orange: #ef8b24;
        --uca-bg: #ffffff;
        --uca-border: #e5e5e5;
        --uca-text: #202123;
        --uca-muted: #777777;
    }

    /* Supprimer le header et les éléments Streamlit inutiles */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    #MainMenu,
    footer {
        display: none !important;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 100% !important;
        padding-top: 0.75rem !important;
        padding-bottom: 1rem !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #f7f7f8 !important;
        border-right: 1px solid #e5e5e5;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0.5rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.45rem;
    }

    .uca-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 2px 12px;
        margin-bottom: 4px;
    }

    .uca-brand-title {
        color: #202123;
        font-size: 16px;
        font-weight: 750;
        line-height: 1.25;
    }

    .uca-brand-subtitle {
        color: #777;
        font-size: 11px;
        margin-top: 4px;
    }

    .sidebar-section {
        color: #777;
        font-size: 12px;
        font-weight: 650;
        padding: 12px 4px 4px;
    }

    [data-testid="stSidebar"] .stButton > button {
        min-height: 36px;
        border-radius: 8px;
        border: 1px solid transparent;
        box-shadow: none;
        font-weight: 450;
        text-align: left;
        transition: background 0.15s ease;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: #e9e9e9;
        border-color: transparent;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #e5e5e5;
        color: #202123;
        border-color: transparent;
    }

    /* Bouton de menu conversation ⋯ */
    [data-testid="stPopover"] > button {
        min-width: 34px !important;
        width: 34px !important;
        min-height: 34px !important;
        height: 34px !important;
        padding: 0 !important;
        border: none !important;
        border-radius: 8px !important;
        background: transparent !important;
        box-shadow: none !important;
        font-size: 0 !important;
        justify-content: center !important;
    }

    [data-testid="stPopover"] > button:hover {
        background: #e5e5e5 !important;
    }

    [data-testid="stPopover"] > button svg {
        display: none !important;
    }

    [data-testid="stPopover"] > button::after {
        content: "⋯";
        color: #444;
        font-size: 23px;
        line-height: 1;
    }

    /* Contenu général */
    .page-title {
        font-size: 25px;
        font-weight: 750;
        color: var(--uca-dark);
        margin: 4px 0 18px;
    }

    .metric-card {
        background: #fff;
        border: 1px solid var(--uca-border);
        border-radius: 14px;
        padding: 18px;
        min-height: 120px;
    }

    .metric-label {
        color: #777;
        font-size: 13px;
        font-weight: 600;
    }

    .metric-value {
        color: var(--uca-blue);
        font-size: 29px;
        font-weight: 800;
        margin-top: 8px;
    }

    .metric-note {
        color: #8994a7;
        font-size: 11px;
        margin-top: 5px;
    }

    .panel {
        background: white;
        border: 1px solid var(--uca-border);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
    }

    /* Connexion */
    .login-heading {
        max-width: 760px;
        margin: 3vh auto 20px;
        text-align: center;
    }

    .login-card {
        background: white;
        border: 1px solid var(--uca-border);
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 8px 30px rgba(20, 45, 80, 0.05);
    }

    .st-key-login_card {
        background: white;
        border: 1px solid var(--uca-border);
        border-radius: 20px;
        padding: 26px;
        box-shadow: 0 8px 30px rgba(20, 45, 80, 0.05);
    }

    .st-key-login_card [data-testid="stForm"] {
        border: none;
        padding: 0;
    }

    .st-key-login_card [data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }

    .small-muted {
        color: #777;
        font-size: 12px;
    }

    /* Accueil du chatbot */
    .chat-welcome {
        border: none;
        background: transparent;
        text-align: center;
        padding: 35px 12px 24px;
        margin: 8px 0 12px;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        border: none;
        box-shadow: none;
    }

    .stButton > button {
        border-radius: 9px;
        font-weight: 550;
        min-height: 38px;
    }

    div[data-testid="stForm"] {
        border: none;
    }

    @media (max-width: 800px) {
        [data-testid="stMainBlockContainer"] {
            padding: 0.5rem !important;
        }

        .chat-welcome {
            padding: 20px 4px;
        }

        .st-key-login_card {
            padding: 18px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. SESSION
# ============================================================

DEFAULT_STATE = {
    "token": None,
    "user": None,
    "page": "Chat",
    "active_conversation_id": None,
    "conversations": [],
    "messages": [],
    "login_error": None,
    "chat_draft": "",
    "pending_delete_conversation_id": None,
    "pending_delete_conversation_title": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# 4. OUTILS API
# ============================================================

def api_headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    token = st.session_state.get("token")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def api_request(
    method: str,
    path: str,
    *,
    json: Any = None,
    data: Any = None,
    files: Any = None,
    timeout: int = REQUEST_TIMEOUT,
    authenticated: bool = True,
) -> requests.Response:
    headers = (
        api_headers()
        if authenticated
        else {"Accept": "application/json"}
    )

    return requests.request(
        method=method,
        url=f"{API_URL}{path}",
        headers=headers,
        json=json,
        data=data,
        files=files,
        timeout=timeout,
    )


def response_json(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return {
            "detail": response.text or f"HTTP {response.status_code}"
        }


def get_error_message(response: requests.Response) -> str:
    body = response_json(response)

    if isinstance(body, dict):
        detail = (
            body.get("detail")
            or body.get("message")
            or body.get("error")
        )

        if isinstance(detail, list):
            return "; ".join(
                str(item.get("msg", item))
                if isinstance(item, dict)
                else str(item)
                for item in detail
            )

        if detail:
            return str(detail)

    return f"Erreur HTTP {response.status_code}"


def get_first(
    data: Any,
    *keys: str,
    default: Any = None,
) -> Any:
    if not isinstance(data, dict):
        return default

    for key in keys:
        value = data.get(key)
        if value is not None:
            return value

    return default


def normalize_role(user: dict[str, Any]) -> str:
    raw = str(
        get_first(
            user,
            "role",
            "user_role",
            "type",
            default="user",
        )
    ).lower()

    if "admin" in raw or "administrateur" in raw:
        return "admin"

    if "enseign" in raw or "teacher" in raw or "prof" in raw:
        return "enseignant"

    if (
        "student" in raw
        or "etudiant" in raw
        or "étudiant" in raw
    ):
        return "etudiant"

    return raw


def display_name(user: dict[str, Any] | None) -> str:
    if not user:
        return "Utilisateur"

    full_name = get_first(
        user,
        "full_name",
        "name",
        "nom_complet",
    )

    if full_name:
        return str(full_name)

    first = get_first(
        user,
        "first_name",
        "prenom",
        "prénom",
        default="",
    )
    last = get_first(user, "last_name", "nom", default="")

    combined = f"{first} {last}".strip()

    return combined or str(
        get_first(
            user,
            "username",
            "email",
            default="Utilisateur",
        )
    )


def safe_get(path: str) -> Any:
    try:
        response = api_request("GET", path)

        if response.ok:
            return response_json(response)

    except requests.RequestException:
        pass

    return None


def extract_list(
    payload: Any,
    *possible_keys: str,
) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [
            item for item in payload
            if isinstance(item, dict)
        ]

    if isinstance(payload, dict):
        for key in possible_keys:
            value = payload.get(key)

            if isinstance(value, list):
                return [
                    item for item in value
                    if isinstance(item, dict)
                ]

    return []


def request_first_success(
    attempts: list[tuple[str, str, dict[str, Any] | None]],
    *,
    timeout: int = REQUEST_TIMEOUT,
) -> tuple[requests.Response | None, str]:
    last_message = "Aucune route API compatible n'a répondu."

    for method, path, payload in attempts:
        try:
            response = api_request(
                method,
                path,
                json=payload,
                timeout=timeout,
            )

            if response.ok:
                return response, ""

            last_message = (
                f"{method} {path} : "
                f"{get_error_message(response)}"
            )

        except requests.RequestException as exc:
            last_message = str(exc)

    return None, last_message


# ============================================================
# 5. AUTHENTIFICATION
# ============================================================

def login_request(
    identifier: str,
    password: str,
) -> tuple[str | None, str | None]:
    attempts = [
        ("/auth/login", "json"),
        ("/auth/token", "form"),
    ]

    last_error = (
        "Identifiants invalides ou route d'authentification indisponible."
    )

    for endpoint, mode in attempts:
        try:
            if mode == "json":
                response = api_request(
                    "POST",
                    endpoint,
                    json={
                        "username": identifier,
                        "email": identifier,
                        "password": password,
                    },
                    authenticated=False,
                )
            else:
                response = api_request(
                    "POST",
                    endpoint,
                    data={
                        "username": identifier,
                        "password": password,
                    },
                    authenticated=False,
                )

            body = response_json(response)

            if response.ok and isinstance(body, dict):
                token = get_first(body, "access_token", "token")

                if token:
                    return str(token), None

            last_error = get_error_message(response)

        except requests.RequestException as exc:
            last_error = f"Impossible de contacter l'API : {exc}"

    return None, last_error


def load_current_user() -> dict[str, Any] | None:
    body = safe_get("/auth/me")

    if isinstance(body, dict):
        nested = body.get("user")
        return nested if isinstance(nested, dict) else body

    return None


def logout() -> None:
    for key, value in DEFAULT_STATE.items():
        st.session_state[key] = value

    st.rerun()


# ============================================================
# 6. OUTILS INTERFACE
# ============================================================

def render_logo(width: int = 100) -> bool:
    for path in LOGO_PATHS:
        if path.exists():
            st.image(str(path), width=width)
            return True

    st.markdown(
        "<div style='font-size:40px;text-align:center'>🎓</div>",
        unsafe_allow_html=True,
    )
    return False


def page_header(
    eyebrow: str,
    title: str,
    subtitle: str = "",
) -> None:
    """Les anciens headers sont volontairement désactivés."""
    return


def metric_card(
    label: str,
    value: Any,
    note: str = "",
) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 7. CONNEXION
# ============================================================

def render_login() -> None:
    st.markdown(
        """
        <div class="login-heading">
            <div style="
                color:#ef8b24;
                font-size:11px;
                font-weight:800;
                letter-spacing:1.8px;
                margin-bottom:10px">
                UNIVERSITÉ CADI AYYAD
            </div>
            <div style="
                font-size:30px;
                font-weight:800;
                color:#0b2545;
                line-height:1.25">
                Bienvenue sur votre assistant universitaire
            </div>
            <div style="
                color:#6b778c;
                font-size:14px;
                margin-top:10px">
                Connectez-vous pour accéder à votre espace intelligent.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 1.15, 1])

    with center:
        with st.container(key="login_card"):
            render_logo(115)

            st.markdown(
                """
                <div style="
                    font-size:23px;
                    font-weight:800;
                    color:#123b69;
                    margin:12px 0 4px">
                    Connexion
                </div>
                <div style="
                    font-size:13px;
                    color:#6b778c;
                    margin-bottom:16px">
                    Étudiants, enseignants et administrateurs
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("login_form", clear_on_submit=False):
                identifier = st.text_input(
                    "Adresse e-mail ou nom d'utilisateur",
                    placeholder="exemple@uca.ac.ma",
                )

                password = st.text_input(
                    "Mot de passe",
                    type="password",
                    placeholder="Saisissez votre mot de passe",
                )

                submitted = st.form_submit_button(
                    "Se connecter",
                    type="primary",
                    use_container_width=True,
                )

            if st.session_state.get("login_error"):
                st.error(st.session_state.login_error)

            if submitted:
                if not identifier.strip() or not password:
                    st.warning(
                        "Veuillez renseigner votre identifiant et votre mot de passe."
                    )
                else:
                    with st.spinner("Connexion en cours..."):
                        token, error = login_request(
                            identifier.strip(),
                            password,
                        )

                    if token:
                        st.session_state.token = token

                        user = load_current_user()

                        if not user:
                            user = {
                                "username": identifier.strip(),
                                "role": "user",
                            }

                        st.session_state.user = user
                        st.session_state.login_error = None
                        st.session_state.conversations = []
                        st.session_state.messages = []
                        st.session_state.active_conversation_id = None

                        st.session_state.page = (
                            "Dashboard"
                            if normalize_role(user) == "admin"
                            else "Chat"
                        )

                        st.rerun()

                    else:
                        st.session_state.login_error = error
                        st.rerun()

            st.markdown(
                """
                <div class="small-muted"
                     style="margin-top:18px;text-align:center">
                    UCA · Assistant universitaire intelligent
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# 8. CONVERSATIONS
# ============================================================

def fetch_conversations(
    force: bool = False,
) -> list[dict[str, Any]]:
    if not force and st.session_state.get("conversations"):
        return st.session_state.conversations

    payload = safe_get("/chat/conversations")

    conversations = extract_list(
        payload,
        "conversations",
        "items",
        "results",
        "data",
    )

    st.session_state.conversations = conversations

    return conversations


def conversation_title(item: dict[str, Any]) -> str:
    return str(
        get_first(
            item,
            "title",
            "name",
            "subject",
            "first_message",
            default="Nouvelle conversation",
        )
    )


def conversation_id(item: dict[str, Any]) -> Any:
    return get_first(item, "id", "conversation_id", "uuid")


def create_conversation() -> Any:
    for payload in (
        {"title": "Nouvelle conversation"},
        {},
    ):
        try:
            response = api_request(
                "POST",
                "/chat/conversations",
                json=payload,
            )

            if response.ok:
                body = response_json(response)

                if isinstance(body, dict):
                    nested = body.get("conversation")

                    if isinstance(nested, dict):
                        body = nested

                    cid = conversation_id(body)

                    if cid is not None:
                        st.session_state.active_conversation_id = cid
                        st.session_state.messages = []
                        st.session_state.chat_draft = ""
                        st.session_state["pending_delete_conversation_id"] = None

                        fetch_conversations(force=True)

                        return cid

        except requests.RequestException:
            continue

    # Permet de conserver un mode sans conversation persistée si
    # le backend ne propose pas encore la création de conversations.
    st.session_state.active_conversation_id = None
    st.session_state.messages = []

    return None


def load_messages(cid: Any) -> list[dict[str, Any]]:
    if cid is None:
        return []

    payload = safe_get(f"/chat/conversations/{cid}/messages")

    messages = extract_list(
        payload,
        "messages",
        "items",
        "results",
        "data",
    )

    normalized = []

    for item in messages:
        role = str(
            get_first(
                item,
                "role",
                "sender",
                "message_role",
                default="assistant",
            )
        ).lower()

        content = get_first(
            item,
            "content",
            "message",
            "text",
            "answer",
            default="",
        )

        if role in (
            "user",
            "human",
            "student",
            "etudiant",
            "étudiant",
            "enseignant",
        ):
            role = "user"
        else:
            role = "assistant"

        normalized.append(
            {
                "role": role,
                "content": str(content),
            }
        )

    return normalized


def rename_conversation(cid: Any, title: str) -> bool:
    try:
        response = api_request(
            "PATCH",
            f"/chat/conversations/{cid}",
            json={"title": title},
        )

        return response.ok

    except requests.RequestException:
        return False


def delete_conversation(cid: Any) -> bool:
    try:
        response = api_request(
            "DELETE",
            f"/chat/conversations/{cid}",
        )

        return response.ok

    except requests.RequestException:
        return False


# ============================================================
# 9. SIDEBAR — NAVIGATION ET MENU CHATGPT
# ============================================================

def render_sidebar() -> None:
    user = st.session_state.user or {}
    role = normalize_role(user)

    with st.sidebar:
        # Logo et identité
        st.markdown("<div class='uca-brand'>", unsafe_allow_html=True)

        logo_found = False

        for logo_path in LOGO_PATHS:
            if logo_path.exists():
                st.image(str(logo_path), width=43)
                logo_found = True
                break

        if not logo_found:
            st.markdown("🎓")

        st.markdown(
            """
            <div>
                <div class="uca-brand-title">UCA Assistant</div>
                <div class="uca-brand-subtitle">
                    Assistant universitaire intelligent
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # Nouvelle conversation
        if st.button(
            "＋  Nouvelle conversation",
            key="new_conversation",
            use_container_width=True,
        ):
            create_conversation()
            st.session_state.page = "Chat"
            st.rerun()

        # Navigation administrateur
        if role == "admin":
            st.markdown(
                "<div class='sidebar-section'>Administration</div>",
                unsafe_allow_html=True,
            )

            nav_items = [
                ("▦", "Dashboard"),
                ("♙", "Utilisateurs"),
                ("▤", "Documents"),
                ("✉", "Chat"),
            ]

            if st.session_state.page not in [
                item[1] for item in nav_items
            ]:
                st.session_state.page = "Dashboard"

            for symbol, nav_item in nav_items:
                if st.button(
                    f"{symbol}  {nav_item}",
                    key=f"admin_nav_{nav_item.lower()}",
                    use_container_width=True,
                    type=(
                        "primary"
                        if st.session_state.page == nav_item
                        else "secondary"
                    ),
                ):
                    st.session_state.page = nav_item
                    st.rerun()

        # Historique
        st.markdown(
            "<div class='sidebar-section'>Conversations</div>",
            unsafe_allow_html=True,
        )

        conversations = fetch_conversations(force=True)

        if not conversations:
            st.caption("Vos conversations apparaîtront ici.")

        for item in conversations[:40]:
            cid = conversation_id(item)

            if cid is None:
                continue

            title = conversation_title(item)
            active = (
                str(cid)
                == str(st.session_state.active_conversation_id)
            )

            title_col, menu_col = st.columns(
                [5.5, 1],
                gap="small",
                vertical_alignment="center",
            )

            with title_col:
                button_title = title

                if len(button_title) > 30:
                    button_title = button_title[:27] + "..."

                if st.button(
                    ("●  " if active else "   ") + button_title,
                    key=f"conversation_{cid}",
                    use_container_width=True,
                    help=title,
                    type="primary" if active else "secondary",
                ):
                    st.session_state.active_conversation_id = cid
                    st.session_state.messages = load_messages(cid)
                    st.session_state.page = "Chat"
                    st.session_state.chat_draft = ""
                    st.session_state["pending_delete_conversation_id"] = None
                    st.rerun()

            with menu_col:
                with st.popover(
                    "⋯",
                    help="Options de la conversation",
                    use_container_width=True,
                ):
                    st.caption("Gérer la conversation")

                    edit_key = f"editing_conversation_{cid}"

                    if st.button(
                        "✎  Renommer",
                        key=f"rename_{cid}",
                        use_container_width=True,
                    ):
                        st.session_state[edit_key] = not (
                            st.session_state.get(edit_key, False)
                        )

                    if st.session_state.get(edit_key, False):
                        with st.form(f"rename_form_{cid}"):
                            new_title = st.text_input(
                                "Nouveau titre",
                                value=title,
                                key=f"rename_title_{cid}",
                            )

                            save_title = st.form_submit_button(
                                "Enregistrer",
                                type="primary",
                                use_container_width=True,
                            )

                        if save_title:
                            if not new_title.strip():
                                st.warning(
                                    "Le titre ne peut pas être vide."
                                )
                            elif rename_conversation(
                                cid,
                                new_title.strip(),
                            ):
                                st.session_state[edit_key] = False
                                fetch_conversations(force=True)
                                st.rerun()
                            else:
                                st.error(
                                    "Renommage impossible. Vérifiez la route API."
                                )

                    if st.button(
                        "🗑  Supprimer",
                        key=f"delete_{cid}",
                        use_container_width=True,
                    ):
                        st.session_state[
                            "pending_delete_conversation_id"
                        ] = cid

                        st.session_state[
                            "pending_delete_conversation_title"
                        ] = title

                        st.rerun()

        # Confirmation de suppression en dehors de la boucle
        pending_id = st.session_state.get(
            "pending_delete_conversation_id"
        )

        if pending_id is not None:
            pending_title = st.session_state.get(
                "pending_delete_conversation_title",
                "cette conversation",
            )

            st.divider()

            st.warning(
                f"Supprimer « {pending_title} » ? "
                "Cette action est irréversible."
            )

            confirm_col, cancel_col = st.columns(2, gap="small")

            with confirm_col:
                if st.button(
                    "Supprimer",
                    key="confirm_delete_conversation",
                    type="primary",
                    use_container_width=True,
                ):
                    if delete_conversation(pending_id):
                        if (
                            str(st.session_state.active_conversation_id)
                            == str(pending_id)
                        ):
                            st.session_state.active_conversation_id = None
                            st.session_state.messages = []

                        st.session_state[
                            "pending_delete_conversation_id"
                        ] = None

                        st.session_state[
                            "pending_delete_conversation_title"
                        ] = None

                        fetch_conversations(force=True)
                        st.rerun()

                    else:
                        st.error(
                            "Suppression impossible. Vérifiez la route API."
                        )

            with cancel_col:
                if st.button(
                    "Annuler",
                    key="cancel_delete_conversation",
                    use_container_width=True,
                ):
                    st.session_state[
                        "pending_delete_conversation_id"
                    ] = None

                    st.session_state[
                        "pending_delete_conversation_title"
                    ] = None

                    st.rerun()

        st.divider()

        with st.expander("Mon compte", expanded=False):
            st.write(f"**Nom :** {display_name(user)}")
            st.write(
                f"**E-mail :** "
                f"{get_first(user, 'email', default='Non renseigné')}"
            )
            st.write(f"**Rôle :** {role.capitalize()}")

        if st.button(
            "↪  Se déconnecter",
            key="logout_button",
            use_container_width=True,
        ):
            logout()


# ============================================================
# 10. DONNÉES ADMINISTRATEUR
# ============================================================

def get_admin_users() -> list[dict[str, Any]]:
    payload = safe_get("/admin/users")

    return extract_list(
        payload,
        "users",
        "items",
        "results",
        "data",
    )


def get_admin_dashboard() -> dict[str, Any]:
    payload = safe_get("/admin/dashboard")

    return payload if isinstance(payload, dict) else {}


def get_documents() -> list[dict[str, Any]]:
    for endpoint in (
        "/documents",
        "/documents/",
        "/admin/documents",
    ):
        payload = safe_get(endpoint)

        if payload is not None:
            docs = extract_list(
                payload,
                "documents",
                "items",
                "results",
                "data",
            )

            if isinstance(payload, list) or docs:
                return docs

    return []


# ============================================================
# 11. DASHBOARD ADMINISTRATEUR
# ============================================================

def render_dashboard() -> None:
    st.markdown(
        "<div class='page-title'>Dashboard</div>",
        unsafe_allow_html=True,
    )

    dashboard = get_admin_dashboard()
    users = get_admin_users()
    documents = get_documents()

    roles = [normalize_role(user) for user in users]

    total_users = get_first(
        dashboard,
        "total_users",
        "users_count",
        "total_utilisateurs",
        default=len(users),
    )

    total_students = get_first(
        dashboard,
        "total_students",
        "students_count",
        "etudiants",
        default=roles.count("etudiant"),
    )

    total_teachers = get_first(
        dashboard,
        "total_teachers",
        "teachers_count",
        "enseignants",
        default=roles.count("enseignant"),
    )

    total_admins = get_first(
        dashboard,
        "total_admins",
        "admins_count",
        "administrateurs",
        default=roles.count("admin"),
    )

    total_docs = get_first(
        dashboard,
        "total_documents",
        "documents_count",
        "docs_count",
        "total_docs",
        default=len(documents),
    )

    if total_docs in (None, "", "—"):
        total_docs = len(documents)

    columns = st.columns(5, gap="medium")

    metrics = [
        ("Utilisateurs", total_users, "Tous les comptes"),
        ("Étudiants", total_students, "Comptes étudiants"),
        ("Enseignants", total_teachers, "Comptes enseignants"),
        ("Administrateurs", total_admins, "Comptes administrateurs"),
        ("Documents", total_docs, "Documents disponibles"),
    ]

    for col, (label, value, note) in zip(columns, metrics):
        with col:
            metric_card(label, value, note)

    st.write("")

    left, right = st.columns([1.2, 0.8], gap="large")

    with left:
        st.subheader("Répartition des utilisateurs")

        if users:
            import pandas as pd

            distribution = {
                "Étudiants": roles.count("etudiant"),
                "Enseignants": roles.count("enseignant"),
                "Administrateurs": roles.count("admin"),
            }

            chart_data = pd.DataFrame(
                {
                    "Type de compte": list(distribution.keys()),
                    "Nombre": list(distribution.values()),
                }
            ).set_index("Type de compte")

            st.bar_chart(chart_data)

        else:
            st.info(
                "Les statistiques apparaîtront lorsque "
                "GET /admin/users renverra les utilisateurs."
            )

    with right:
        st.subheader("État de la plateforme")
        st.metric("Documents enregistrés", total_docs)
        st.metric("Utilisateurs chargés", len(users))
        st.caption("Données fournies par l'API FastAPI.")

        if st.button(
            "↻ Actualiser les statistiques",
            use_container_width=True,
        ):
            st.rerun()

    st.subheader("Comptes récemment visibles")

    if users:
        rows = []

        for item in users[:8]:
            rows.append(
                {
                    "Nom": display_name(item),
                    "E-mail": get_first(item, "email", default="—"),
                    "Rôle": normalize_role(item).capitalize(),
                    "Statut": get_first(
                        item,
                        "is_active",
                        "active",
                        default="—",
                    ),
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info(
            "Aucun utilisateur récupéré. Vérifiez GET /admin/users."
        )


# ============================================================
# 12. GESTION DES UTILISATEURS
# ============================================================

def render_users_management() -> None:
    st.markdown(
        "<div class='page-title'>Gestion des utilisateurs</div>",
        unsafe_allow_html=True,
    )

    users = get_admin_users()

    with st.expander("＋ Ajouter un utilisateur", expanded=False):
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)

            with col1:
                first_name = st.text_input(
                    "Prénom",
                    key="create_first_name",
                )

                last_name = st.text_input(
                    "Nom",
                    key="create_last_name",
                )

                email = st.text_input(
                    "Adresse e-mail",
                    key="create_email",
                )

            with col2:
                role = st.selectbox(
                    "Rôle",
                    ["student", "teacher", "admin"],
                    format_func=lambda value: {
                        "student": "Étudiant",
                        "teacher": "Enseignant",
                        "admin": "Administrateur",
                    }[value],
                    key="create_role",
                )

                password = st.text_input(
                    "Mot de passe provisoire",
                    type="password",
                    key="create_password",
                )

            create = st.form_submit_button(
                "Créer le compte",
                type="primary",
            )

        if create:
            full_name = (
                f"{first_name.strip()} {last_name.strip()}"
            ).strip()

            if (
                not first_name.strip()
                or not last_name.strip()
                or not email.strip()
                or not password
            ):
                st.error(
                    "Le prénom, le nom, l'e-mail et le mot de passe sont obligatoires."
                )

            elif len(password) < 8:
                st.error(
                    "Le mot de passe doit contenir au moins 8 caractères."
                )

            else:
                payload = {
                    "full_name": full_name,
                    "email": email.strip(),
                    "password": password,
                    "role": role,
                }

                response, error = request_first_success(
                    [
                        ("POST", "/admin/users", payload),
                    ]
                )

                if response:
                    st.success("Utilisateur créé.")
                    st.rerun()

                else:
                    st.error(
                        f"La création a échoué. Détail : {error}"
                    )

    # Recherche
    st.subheader(f"Liste des comptes ({len(users)})")

    search_user = st.text_input(
        "Rechercher un utilisateur",
        placeholder="Nom, prénom, e-mail ou rôle...",
        key="search_users",
    ).strip().casefold()

    filtered_users = []

    for user in users:
        full_name = str(
            get_first(
                user,
                "full_name",
                "name",
                "username",
                default="",
            )
        )

        email_value = str(
            get_first(user, "email", default="")
        )

        role_value = normalize_role(user)

        searchable = " ".join(
            [full_name, email_value, role_value]
        ).casefold()

        if not search_user or search_user in searchable:
            filtered_users.append(user)

    st.caption(f"{len(filtered_users)} résultat(s)")

    if not filtered_users:
        st.info("Aucun utilisateur ne correspond à cette recherche.")
        return

    rows = []

    for user in filtered_users:
        rows.append(
            {
                "Nom complet": display_name(user),
                "E-mail": get_first(user, "email", default="—"),
                "Rôle": normalize_role(user).capitalize(),
                "Actif": (
                    "Oui"
                    if bool(
                        get_first(
                            user,
                            "is_active",
                            "active",
                            default=True,
                        )
                    )
                    else "Non"
                ),
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Modifier ou supprimer un compte")

    choices = {
        (
            f"{display_name(user)} — "
            f"{get_first(user, 'email', default='sans e-mail')} "
            f"[ID: {get_first(user, 'id', 'user_id', default='?')}]"
        ): user
        for user in filtered_users
    }

    selected_label = st.selectbox(
        "Sélectionner un compte",
        list(choices.keys()),
        key="selected_user_edit",
    )

    selected = choices[selected_label]

    selected_id = get_first(selected, "id", "user_id")

    if selected_id is None:
        st.warning("L'identifiant de ce compte est introuvable.")
        return

    full_name = str(
        get_first(
            selected,
            "full_name",
            "name",
            default="",
        )
    ).strip()

    name_parts = full_name.split(maxsplit=1)

    default_first = name_parts[0] if name_parts else ""
    default_last = name_parts[1] if len(name_parts) > 1 else ""

    active_default = bool(
        get_first(
            selected,
            "is_active",
            "active",
            default=True,
        )
    )

    current_role = normalize_role(selected)

    role_map = {
        "etudiant": "student",
        "enseignant": "teacher",
        "admin": "admin",
    }

    current_role_api = role_map.get(
        current_role,
        current_role,
    )

    role_options = ["student", "teacher", "admin"]

    role_labels = {
        "student": "Étudiant",
        "teacher": "Enseignant",
        "admin": "Administrateur",
    }

    st.markdown("#### Informations du compte")

    with st.form(f"edit_user_form_{selected_id}"):
        col1, col2 = st.columns(2)

        with col1:
            edit_first = st.text_input(
                "Prénom",
                value=default_first,
                key=f"edit_first_{selected_id}",
            )

            edit_email = st.text_input(
                "Adresse e-mail",
                value=str(
                    get_first(selected, "email", default="")
                ),
                key=f"edit_email_{selected_id}",
            )

        with col2:
            edit_last = st.text_input(
                "Nom",
                value=default_last,
                key=f"edit_last_{selected_id}",
            )

            edit_role = st.selectbox(
                "Rôle",
                role_options,
                format_func=lambda value: role_labels[value],
                index=(
                    role_options.index(current_role_api)
                    if current_role_api in role_options
                    else 0
                ),
                key=f"edit_role_{selected_id}",
            )

        edit_active = st.checkbox(
            "Compte actif",
            value=active_default,
            key=f"edit_active_{selected_id}",
        )

        save = st.form_submit_button(
            "Enregistrer les modifications",
            type="primary",
        )

    if save:
        edited_full_name = (
            f"{edit_first.strip()} {edit_last.strip()}"
        ).strip()

        if not edited_full_name or not edit_email.strip():
            st.error(
                "Le prénom, le nom et l'e-mail sont obligatoires."
            )

        else:
            payload = {
                "full_name": edited_full_name,
                "email": edit_email.strip(),
                "role": edit_role,
                "is_active": edit_active,
            }

            response, error = request_first_success(
                [
                    (
                        "PATCH",
                        f"/admin/users/{selected_id}",
                        payload,
                    ),
                ]
            )

            if response:
                st.success("Compte mis à jour.")
                st.rerun()

            else:
                st.error(
                    f"La modification a échoué. Détail : {error}"
                )

    # Suppression avec confirmation
    st.divider()
    st.markdown("#### Zone de suppression")

    st.warning(
        "La suppression peut désactiver logiquement le compte "
        "selon le fonctionnement du backend."
    )

    confirm_key = f"confirm_delete_user_{selected_id}"

    if st.button(
        "🗑 Supprimer le compte",
        key=f"delete_user_{selected_id}",
    ):
        st.session_state[confirm_key] = True

    if st.session_state.get(confirm_key, False):
        st.warning(
            f"Confirmer la suppression du compte "
            f"« {display_name(selected)} » "
            f"({get_first(selected, 'email', default='sans e-mail')}) ?"
        )

        confirm_col, cancel_col = st.columns(2)

        with confirm_col:
            if st.button(
                "Oui, supprimer",
                type="primary",
                key=f"confirm_yes_user_{selected_id}",
            ):
                response, error = request_first_success(
                    [
                        (
                            "DELETE",
                            f"/admin/users/{selected_id}",
                            None,
                        ),
                    ]
                )

                if response:
                    st.session_state[confirm_key] = False
                    st.success("Compte supprimé.")
                    st.rerun()

                else:
                    st.error(
                        f"La suppression a échoué. Détail : {error}"
                    )

        with cancel_col:
            if st.button(
                "Annuler",
                key=f"confirm_no_user_{selected_id}",
            ):
                st.session_state[confirm_key] = False
                st.rerun()


# ============================================================
# 13. GESTION DES DOCUMENTS
# ============================================================

def render_documents() -> None:
    st.markdown(
        "<div class='page-title'>Documents universitaires</div>",
        unsafe_allow_html=True,
    )

    st.subheader("Importer un document")

    uploaded = st.file_uploader(
        "Choisir un fichier PDF ou TXT",
        type=["pdf", "txt"],
        help="Respectez la limite de taille configurée dans le backend.",
    )

    if uploaded and st.button(
        "Téléverser le document",
        type="primary",
    ):
        try:
            response = api_request(
                "POST",
                "/documents/upload",
                files={
                    "file": (
                        uploaded.name,
                        uploaded.getvalue(),
                        uploaded.type
                        or "application/octet-stream",
                    )
                },
                timeout=CHAT_TIMEOUT,
            )

            if response.ok:
                st.success("Document envoyé au backend.")
                st.rerun()

            else:
                st.error(
                    "Échec du téléversement : "
                    f"{get_error_message(response)}"
                )

        except requests.RequestException as exc:
            st.error(f"Impossible de contacter l'API : {exc}")

    st.divider()
    st.subheader("Documents disponibles")

    docs = get_documents()

    search_doc = st.text_input(
        "Rechercher un document par nom",
        placeholder="Nom ou partie du nom du document...",
        key="search_documents",
    ).strip().casefold()

    filtered_docs = []

    for doc in docs:
        filename = str(
            get_first(
                doc,
                "filename",
                "file_name",
                "name",
                "title",
                default="Document sans nom",
            )
        )

        title = str(
            get_first(doc, "title", default="")
        )

        if not search_doc or search_doc in (
            f"{filename} {title}".casefold()
        ):
            filtered_docs.append(doc)

    st.caption(
        f"{len(filtered_docs)} document(s) trouvé(s) sur {len(docs)}"
    )

    if not filtered_docs:
        st.info(
            "Aucun document ne correspond à la recherche."
            if docs
            else "Aucun document n'a été renvoyé par l'API."
        )
        return

    rows = []

    for doc in filtered_docs:
        rows.append(
            {
                "Nom": get_first(
                    doc,
                    "filename",
                    "file_name",
                    "name",
                    "title",
                    default="Document sans nom",
                ),
                "Statut": get_first(
                    doc,
                    "status",
                    "processing_status",
                    default="—",
                ),
                "Date d'ajout": get_first(
                    doc,
                    "created_at",
                    "uploaded_at",
                    "created_on",
                    default="—",
                ),
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("Supprimer un document")

    doc_choices = {}

    for doc in filtered_docs:
        doc_id = get_first(doc, "id", "document_id")

        if doc_id is None:
            continue

        filename = get_first(
            doc,
            "filename",
            "file_name",
            "name",
            "title",
            default="Document sans nom",
        )

        doc_choices[f"{filename} — ID : {doc_id}"] = doc

    if not doc_choices:
        st.info(
            "Aucun identifiant de document disponible pour la suppression."
        )
        return

    selected_doc_label = st.selectbox(
        "Document à supprimer",
        list(doc_choices.keys()),
        key="selected_doc_delete",
    )

    selected_doc = doc_choices[selected_doc_label]

    selected_doc_id = get_first(
        selected_doc,
        "id",
        "document_id",
    )

    doc_confirm_key = f"confirm_delete_doc_{selected_doc_id}"

    if st.button(
        "🗑 Supprimer le document sélectionné",
        key=f"delete_doc_{selected_doc_id}",
    ):
        st.session_state[doc_confirm_key] = True

    if st.session_state.get(doc_confirm_key, False):
        doc_name = get_first(
            selected_doc,
            "filename",
            "file_name",
            "title",
            "name",
            default="ce document",
        )

        st.warning(
            f"Voulez-vous vraiment supprimer « {doc_name} » ?"
        )

        yes_col, no_col = st.columns(2)

        with yes_col:
            if st.button(
                "Oui, supprimer",
                type="primary",
                key=f"confirm_yes_doc_{selected_doc_id}",
            ):
                response, error = request_first_success(
                    [
                        (
                            "DELETE",
                            f"/admin/documents/{selected_doc_id}",
                            None,
                        ),
                    ]
                )

                if response:
                    st.session_state[doc_confirm_key] = False
                    st.success("Document supprimé.")
                    st.rerun()

                else:
                    st.error(
                        f"La suppression a échoué. Détail : {error}"
                    )

        with no_col:
            if st.button(
                "Annuler",
                key=f"confirm_no_doc_{selected_doc_id}",
            ):
                st.session_state[doc_confirm_key] = False
                st.rerun()


# ============================================================
# 14. CHATBOT
# ============================================================

def send_chat_message(question: str) -> str:
    cid = st.session_state.get("active_conversation_id")

    payload_variants = [
        {"question": question, "conversation_id": cid},
        {"message": question, "conversation_id": cid},
        {"query": question, "conversation_id": cid},
    ]

    last_error = "La route de discussion n'a pas renvoyé de réponse."

    for payload in payload_variants:
        payload = payload.copy()

        if payload.get("conversation_id") is None:
            payload.pop("conversation_id", None)

        try:
            response = api_request(
                "POST",
                "/chat/ask",
                json=payload,
                timeout=CHAT_TIMEOUT,
            )

            body = response_json(response)

            if response.ok and isinstance(body, dict):
                answer = get_first(
                    body,
                    "answer",
                    "response",
                    "message",
                    "content",
                    "text",
                )

                if answer is not None:
                    return str(answer)

                return str(body)

            last_error = get_error_message(response)

            if response.status_code not in (400, 422):
                break

        except requests.RequestException as exc:
            last_error = f"Impossible de contacter le chatbot : {exc}"
            break

    raise RuntimeError(last_error)


def render_chat() -> None:
    user = st.session_state.user or {}
    role = normalize_role(user)

    # Aucun header de page : uniquement l'accueil si le chat est vide.
    if (
        not st.session_state.get("active_conversation_id")
        and not st.session_state.messages
    ):
        st.markdown(
            """
            <div class="chat-welcome">
                <div style="font-size:38px;margin-bottom:14px">🎓</div>
                <div style="
                    font-size:26px;
                    font-weight:650;
                    color:#202123">
                    Comment puis-je vous aider ?
                </div>
                <div style="
                    color:#777;
                    font-size:14px;
                    margin-top:10px">
                    Votre assistant intelligent pour la vie universitaire à l'UCA.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        prompts = [
            "Quels sont les établissements de l'UCA ?",
            "Comment se déroule l'inscription ?",
            "Quelles sont les conditions d'admission ?",
        ]

        prompt_cols = st.columns(3)

        for col, prompt in zip(prompt_cols, prompts):
            with col:
                if st.button(
                    prompt,
                    key=f"prompt_{prompt}",
                    use_container_width=True,
                ):
                    st.session_state.chat_draft = prompt
                    st.rerun()

    # Historique des messages
    for message in st.session_state.messages:
        with st.chat_message(
            message.get("role", "assistant")
        ):
            st.markdown(message.get("content", ""))

    # Saisie du message
    question = st.chat_input("Posez votre question...")

    draft = st.session_state.get("chat_draft", "")

    if draft and not question:
        question = draft
        st.session_state.chat_draft = ""

    if not question:
        return

    question = question.strip()

    if not question:
        return

    # Créer une conversation avant le premier message.
    if st.session_state.get("active_conversation_id") is None:
        create_conversation()

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("L'assistant prépare sa réponse..."):
            try:
                answer = send_chat_message(question)

            except RuntimeError as exc:
                answer = (
                    f"**Une erreur est survenue :** {exc}\n\n"
                    "Vérifiez que FastAPI est lancé et que "
                    "`POST /chat/ask` accepte le champ `question` "
                    "ou `message`."
                )

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    fetch_conversations(force=True)

    st.rerun()


# ============================================================
# 15. APPLICATION PRINCIPALE
# ============================================================

def main() -> None:
    if not st.session_state.get("token"):
        render_login()
        return

    if not st.session_state.get("user"):
        st.session_state.user = (
            load_current_user() or {"role": "user"}
        )

    user = st.session_state.user or {}
    role = normalize_role(user)

    # Bloquer l'administration pour les utilisateurs non-admin.
    admin_pages = (
        "Dashboard",
        "Utilisateurs",
        "Documents",
    )

    if role != "admin" and st.session_state.page in admin_pages:
        st.session_state.page = "Chat"

    render_sidebar()

    current_page = st.session_state.page

    if current_page == "Dashboard" and role == "admin":
        render_dashboard()

    elif current_page == "Utilisateurs" and role == "admin":
        render_users_management()

    elif current_page == "Documents" and role == "admin":
        render_documents()

    else:
        render_chat()


if __name__ == "__main__":
    main()
