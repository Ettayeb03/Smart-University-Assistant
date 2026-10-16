
from sqlalchemy import inspect, text

from backend.core.database import engine


def main():
    with engine.begin() as connection:
        inspector = inspect(connection)

        indexes = inspector.get_indexes("users")
        index_names = {index["name"] for index in indexes}

        if "ix_users_email" in index_names:
            connection.execute(
                text("DROP INDEX ix_users_email")
            )
            print("Ancien index ix_users_email supprimé.")

        connection.execute(
            text(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email_active
                ON users (email)
                WHERE is_deleted = FALSE
                """
            )
        )
        print("Index unique partiel créé ou déjà présent.")

    print("Migration terminée.")


if __name__ == "__main__":
    main()
