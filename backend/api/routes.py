
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import get_db
from backend.core.security import hash_password
from backend.models.user import User
from backend.schemas.user import (
    UserCreate,
    UserResponse,
    UserCreateAdmin,
    UserUpdateAdmin,
)
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordRequestForm

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.permissions import get_current_user as get_authenticated_user
from backend.models.document import Document
from backend.schemas.document import (
    DocumentResponse,
    DocumentUpdateAdmin,
)
from backend.core.security import (
    create_access_token,
    decode_access_token,
    verify_password,
)

from backend.services.document_extractor import (
    DocumentExtractionError,
    extract_text_from_file,
)

from backend.schemas.user import TokenResponse, UserLogin
from backend.core.oauth2 import oauth2_scheme
from backend.core.permissions import require_admin

import os
import uuid
from pathlib import Path

from fastapi import File, UploadFile
from sqlalchemy.exc import SQLAlchemyError

from backend.core.permissions import require_admin
from datetime import datetime, timezone

router = APIRouter()

@router.get("/")
def root():
    return {
        "message": f"Bienvenue dans {settings.APP_NAME}",
        "status": "running",
        "version": settings.APP_VERSION,
    }


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "smart-university-assistant",
    }


@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(
            User.email == user_data.email,
            User.is_deleted.is_(False),
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette adresse e-mail est déjà utilisée.",
        )

    new_user = User(
        full_name=user_data.full_name,
        email=str(user_data.email),
        hashed_password=hash_password(user_data.password),
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette adresse e-mail est déjà utilisée.",
        )

    return new_user


@router.post("/auth/login", response_model=TokenResponse)
def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.email == str(credentials.email)
    ).first()

    if not user or not verify_password(
        credentials.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active or user.is_deleted:        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte est désactivé.",
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/auth/token", response_model=TokenResponse)
def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte est désactivé.",
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get("/auth/me", response_model=UserResponse)
def read_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton invalide ou expiré.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, TypeError, ValueError):
        raise credentials_error

    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active or user.is_deleted:
        raise credentials_error

    return user



@router.get("/admin/dashboard")
def admin_dashboard(
    current_user: User = Depends(require_admin),
):
    return {
        "message": "Bienvenue dans le tableau de bord administrateur.",
        "user_id": current_user.id,
        "role": current_user.role,
    }

@router.get("/admin/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    users = (
        db.query(User)
        .filter(User.is_deleted.is_(False))
        .order_by(User.id.asc())
        .all()
    )
    return users

@router.post(
    "/admin/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_admin(
    user_data: UserCreateAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    existing_user = (
        db.query(User)
        .filter(
            User.email == user_data.email,
            User.is_deleted.is_(False),
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur avec cet e-mail existe déjà.",
        )

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossible de créer cet utilisateur : e-mail déjà utilisé.",
        )

    return new_user

@router.patch("/admin/users/{user_id}", response_model=UserResponse)
def update_user_admin(
    user_id: int,
    user_data: UserUpdateAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.is_deleted.is_(False),
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable.",
        )

    updates = user_data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune donnée à modifier.",
        )

    if "email" in updates and updates["email"] != user.email:
        existing_user = (
            db.query(User)
            .filter(
                User.email == updates["email"],
                User.is_deleted.is_(False),
                User.id != user_id,
            )
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cet e-mail est déjà utilisé.",
            )

    for field, value in updates.items():
        setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflit lors de la modification de l'utilisateur.",
        )

    return user

@router.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.is_deleted.is_(False),
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable.",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas supprimer votre propre compte administrateur.",
        )

    user.is_deleted = True
    user.deleted_at = datetime.now(timezone.utc)
    user.deleted_by = current_user.id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossible de supprimer cet utilisateur.",
        )

@router.get("/documents", response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_authenticated_user),
):
    documents = (
    db.query(Document)
    .filter(Document.is_deleted.is_(False))
    .order_by(Document.created_at.desc())
    .all()
    )
    return documents


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_authenticated_user),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.is_deleted.is_(False),
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document introuvable.",
        )

    return document

@router.patch(
    "/admin/documents/{document_id}",
    response_model=DocumentResponse,
)
def update_document_admin(
    document_id: int,
    document_data: DocumentUpdateAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.is_deleted.is_(False),
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document introuvable.",
        )

    updates = document_data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="Aucune donnée à modifier.",
        )

    for field, value in updates.items():
        setattr(document, field, value)

    try:
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la modification du document.",
        )

    return document


@router.delete(
    "/admin/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document_admin(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.is_deleted.is_(False),
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document introuvable.",
        )

    document.is_deleted = True
    document.deleted_at = datetime.now(timezone.utc)
    document.deleted_by = current_user.id

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la suppression du document.",
        )

    return None

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 Mo

ALLOWED_EXTENSIONS = {".pdf", ".txt"}

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOCUMENTS_DIR = PROJECT_ROOT / "storage" / "documents"

@router.post("/documents/upload", response_model=DocumentResponse, status_code=201)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Nom de fichier invalide.",
        )

    original_filename = Path(file.filename).name
    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Format non autorisé. Utilisez PDF ou TXT.",
        )

    content = file.file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Le fichier est vide.",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="La taille maximale autorisée est de 10 Mo.",
        )

    if extension == ".pdf" and not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Le fichier n'est pas un PDF valide.",
        )

    if extension == ".txt":
        try:
            content.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Le fichier TXT doit être encodé en UTF-8.",
            )

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    # Nom généré par le serveur pour éviter les collisions
    stored_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = DOCUMENTS_DIR / stored_filename

    try:
        with file_path.open("wb") as stored_file:
            stored_file.write(content)

        document = Document(
            title=Path(original_filename).stem[:255] or "Document",
            filename=original_filename[:255],
            file_type=extension.lstrip("."),
            file_size=len(content),
            storage_path=str(file_path.relative_to(PROJECT_ROOT)),
            status="pending",
            uploaded_by=current_user.id,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()

        if file_path.exists():
            try:
                file_path.unlink()
            except OSError:
                pass

        raise HTTPException(
            status_code=500,
            detail="Erreur lors de l'enregistrement du document.",
        )

    finally:
        file.file.close()

@router.post(
    "/documents/{document_id}/process",
    response_model=DocumentResponse,
)

def process_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    # 1. Rechercher un document non supprimé
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.is_deleted.is_(False),
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document introuvable.",
        )

    # 2. Construire le chemin du fichier
    file_path = PROJECT_ROOT / document.storage_path

    if not file_path.is_file():
        document.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=404,
            detail="Le fichier physique du document est introuvable.",
        )

    # 3. Indiquer que le traitement commence
    document.status = "processing"
    db.commit()

    # 4. Extraire le texte
    try:
        extracted_text = extract_text_from_file(file_path)

        document.extracted_text = extracted_text
        document.status = "processed"

        db.commit()
        db.refresh(document)

        return document

    except DocumentExtractionError as exc:
        db.rollback()

        document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.is_deleted.is_(False),
            )
            .first()
        )

        if document is not None:
            document.status = "failed"
            db.commit()

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    except Exception as exc:
        db.rollback()

        document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.is_deleted.is_(False),
            )
            .first()
        )

        if document is not None:
            document.status = "failed"
            db.commit()

        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors du traitement du document.",
        ) from exc

from backend.schemas.chat import ChatAskRequest, ChatAskResponse
from backend.services.rag.rag_service import RAGService


@router.post("/chat/ask", response_model=ChatAskResponse)
def ask_chatbot(
    request: ChatAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La question ne peut pas ?tre vide.",
        )

    try:
        # Retrouver une conversation appartenant ? l'utilisateur.
        if request.conversation_id is not None:
            conversation = (
                db.query(Conversation)
                .filter(
                    Conversation.id == request.conversation_id,
                    Conversation.user_id == current_user.id,
                )
                .first()
            )

            if conversation is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation introuvable.",
                )

        else:
            # Cr?er une conversation automatiquement.
            title = question[:197] + "..." if len(question) > 200 else question
            conversation = Conversation(
                user_id=current_user.id,
                title=title,
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # Enregistrer la question avant l'appel au RAG.
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=question,
        )
        db.add(user_message)
        db.commit()

        # R?cup?rer les messages pr?c?dents pour comprendre les questions de suivi.
        previous_messages = (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation.id,
                Message.id != user_message.id,
            )
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(6)
            .all()
        )

        history = [
            {"role": message.role, "content": message.content}
            for message in reversed(previous_messages)
        ]

        # G?n?rer la r?ponse ? partir des documents index?s et de l'historique.
        rag_service = RAGService()
        result = rag_service.answer(
            question=question,
            top_k=request.top_k,
            history=history,
        )

        # Enregistrer la r?ponse et ses sources uniquement si le RAG r?ussit.
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result["answer"],
            sources=result.get("sources", []) or [],
        )
        conversation.updated_at = datetime.now(timezone.utc)

        db.add(assistant_message)
        db.commit()
        db.refresh(conversation)

        return {
            "answer": result["answer"],
            "sources": result.get("sources", []) or [],
            "conversation_id": conversation.id,
        }

    except HTTPException:
        db.rollback()
        raise

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()
        import logging
        logging.getLogger(__name__).exception(
            "Erreur lors de l'enregistrement ou de la g?n?ration du message."
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur est survenue lors du traitement du message.",
        ) from exc

from backend.models.conversation import Conversation
from backend.models.message import Message
from backend.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    MessageResponse,
)


@router.post(
    "/chat/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title.strip() or "Nouvelle conversation",
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get(
    "/chat/conversations",
    response_model=list[ConversationResponse],
)
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


@router.get(
    "/chat/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def list_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation introuvable.",
        )

    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .all()
    )


from backend.schemas.conversation import ConversationUpdate


@router.patch(
    "/chat/conversations/{conversation_id}",
    response_model=ConversationResponse,
)
def update_conversation(
    conversation_id: int,
    conversation_data: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation introuvable.",
        )

    title = conversation_data.title.strip()
    if not title:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Le nom de la conversation ne peut pas ?tre vide.",
        )

    conversation.title = title
    conversation.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(conversation)
    return conversation


@router.delete("/chat/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation introuvable.",
        )

    db.delete(conversation)
    db.commit()

    return {"message": "Conversation supprim?e avec succ?s."}
