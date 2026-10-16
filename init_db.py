from backend.core.database import Base, engine
from backend.models.user import User
from backend.models.document import Document
from backend.models.conversation import Conversation
from backend.models.message import Message

Base.metadata.create_all(bind=engine)

print("Tables créées ou déjà existantes :")
for table_name in sorted(Base.metadata.tables):
    print(f"- {table_name}")

print("Initialisation terminée.")
