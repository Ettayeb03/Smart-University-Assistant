import streamlit as st


def render_admin_pages(api_request, user):
    """Affiche les pages Documents, Utilisateurs et Tableau de bord."""
    role = user.get("role", "student")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ESPACE UNIVERSITAIRE")

    pages = ["Chat", "Documents"]
    if role == "admin":
        pages += ["Tableau de bord", "Utilisateurs"]

    if "app_page" not in st.session_state:
        st.session_state.app_page = "Chat"

    # Revenir au Chat si le rôle ne permet plus d'accéder à la page choisie.
    if st.session_state.app_page not in pages:
        st.session_state.app_page = "Chat"

    selected = st.sidebar.radio(
        "Navigation",
        pages,
        key="app_page",
    )

    if selected == "Chat":
        return False

    st.markdown("## " + selected)
    st.caption("Smart University Assistant · Université Cadi Ayyad")
    st.divider()

    if selected == "Documents":
        render_documents(api_request, role)
    elif selected == "Tableau de bord" and role == "admin":
        render_dashboard(api_request)
    elif selected == "Utilisateurs" and role == "admin":
        render_users(api_request)

    return True


def render_documents(api_request, role):
    if role == "admin":
        st.subheader("Importer un document")
        uploaded = st.file_uploader(
            "Choisir un PDF, RTF ou une image",
            type=["pdf", "rtf", "png", "jpg", "jpeg"],
        )
        if uploaded and st.button("Importer le document", type="primary"):
            try:
                result = api_request(
                    "POST",
                    "/documents/upload",
                    files={
                        "file": (
                            uploaded.name,
                            uploaded.getvalue(),
                            uploaded.type or "application/octet-stream",
                        )
                    },
                )
                if result is not None:
                    st.success("Import envoyé. Actualisez la liste ci-dessous.")
                    st.rerun()
            except Exception as exc:
                st.error(f"Échec de l'import : {exc}")

    st.subheader("Documents disponibles")
    try:
        documents = api_request("GET", "/documents")
        if not isinstance(documents, list):
            st.info("Aucun document à afficher, ou réponse API inattendue.")
            return
        if not documents:
            st.info("Aucun document disponible.")
            return

        for doc in documents:
            doc_id = doc.get("id")
            title = doc.get("title") or doc.get("filename") or f"Document {doc_id}"
            status = doc.get("status", "inconnu")
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                col1.markdown(f"**{title}**")
                col1.caption(
                    f"Type : {doc.get('file_type', '—')} · "
                    f"Statut : {status} · ID : {doc_id}"
                )
                if role == "admin":
                    if col2.button("Traiter", key=f"process_doc_{doc_id}"):
                        try:
                            api_request("POST", f"/documents/{doc_id}/process")
                            st.success(f"Traitement demandé pour {title}.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Échec du traitement : {exc}")

                    if st.button("Supprimer", key=f"delete_doc_{doc_id}"):
                        try:
                            api_request("DELETE", f"/admin/documents/{doc_id}")
                            st.success("Document supprimé.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Échec de la suppression : {exc}")
    except Exception as exc:
        st.error(f"Impossible de charger les documents : {exc}")


def render_dashboard(api_request):
    try:
        data = api_request("GET", "/admin/dashboard")
        if not isinstance(data, dict):
            st.warning("La réponse du tableau de bord n'est pas au format attendu.")
            st.json(data)
            return

        # Affiche les indicateurs réellement renvoyés par l'API.
        numeric_items = [
            (key, value)
            for key, value in data.items()
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        ]
        if numeric_items:
            cols = st.columns(min(4, len(numeric_items)))
            for i, (key, value) in enumerate(numeric_items):
                cols[i % len(cols)].metric(key.replace("_", " ").title(), value)

        st.subheader("Données du tableau de bord")
        st.json(data)
    except Exception as exc:
        st.error(f"Impossible de charger le tableau de bord : {exc}")


def render_users(api_request):
    st.subheader("Créer un utilisateur")
    with st.form("create_user_form", clear_on_submit=True):
        full_name = st.text_input("Nom complet")
        email = st.text_input("Adresse e-mail")
        password = st.text_input("Mot de passe (8 caractères minimum)", type="password")
        role = st.selectbox("Rôle", ["student", "teacher", "admin"])
        submitted = st.form_submit_button("Créer l'utilisateur")

    if submitted:
        if not full_name.strip() or not email.strip() or len(password) < 8:
            st.error("Vérifiez les champs et utilisez un mot de passe d'au moins 8 caractères.")
        else:
            try:
                result = api_request(
                    "POST",
                    "/admin/users",
                    json={
                        "full_name": full_name.strip(),
                        "email": email.strip(),
                        "password": password,
                        "role": role,
                    },
                )
                if result is not None:
                    st.success("Utilisateur créé.")
                    st.rerun()
            except Exception as exc:
                st.error(f"Échec de la création : {exc}")

    st.divider()
    st.subheader("Utilisateurs enregistrés")
    try:
        users = api_request("GET", "/admin/users")
        if not isinstance(users, list):
            st.warning("La réponse de l'API n'est pas une liste d'utilisateurs.")
            st.json(users)
            return

        for item in users:
            uid = item.get("id")
            name = item.get("full_name") or "Sans nom"
            with st.container(border=True):
                st.markdown(f"**{name}**")
                st.caption(
                    f"{item.get('email', '—')} · "
                    f"Rôle : {item.get('role', '—')} · ID : {uid}"
                )
                col1, col2 = st.columns(2)
                active = bool(item.get("is_active", True))
                new_active = col1.toggle(
                    "Compte actif",
                    value=active,
                    key=f"user_active_{uid}",
                )
                if new_active != active:
                    try:
                        api_request(
                            "PATCH",
                            f"/admin/users/{uid}",
                            json={"is_active": new_active},
                        )
                        st.success("Statut du compte mis à jour.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Échec de la mise à jour : {exc}")

                if col2.button("Supprimer", key=f"delete_user_{uid}"):
                    st.session_state[f"confirm_user_delete_{uid}"] = True

                if st.session_state.get(f"confirm_user_delete_{uid}", False):
                    st.warning("Confirmer la suppression de cet utilisateur ?")
                    yes, no = st.columns(2)
                    if yes.button("Confirmer", key=f"confirm_user_{uid}"):
                        try:
                            api_request("DELETE", f"/admin/users/{uid}")
                            st.session_state[f"confirm_user_delete_{uid}"] = False
                            st.success("Utilisateur supprimé.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Échec de la suppression : {exc}")
                    if no.button("Annuler", key=f"cancel_user_{uid}"):
                        st.session_state[f"confirm_user_delete_{uid}"] = False
                        st.rerun()
    except Exception as exc:
        st.error(f"Impossible de charger les utilisateurs : {exc}")
