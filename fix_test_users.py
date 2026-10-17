
from pwdlib import PasswordHash

# Utiliser le même mécanisme de hachage que le backend
password_hasher = PasswordHash.recommended()

users = [
    ("Yassine Alaoui", "yassine", "student"),
    ("Salma Bennani", "salma", "student"),
    ("Amine El Idrissi", "amine", "student"),
    ("Sara Tazi", "sara", "student"),
    ("Hamza Berrada", "hamza", "student"),
    ("Imane Chraibi", "imane", "student"),
    ("Othmane Fassi", "othmane", "student"),
    ("Ghita Lahlou", "ghita", "student"),
    ("Mehdi Benjelloun", "mehdi", "student"),
    ("Lina Amrani", "lina", "student"),
    ("Nadia El Mansouri", "nadia", "teacher"),
    ("Karim Belkacem", "karim", "teacher"),
    ("Hajar Ouazzani", "hajar", "teacher"),
    ("Rachid Chafai", "rachid", "teacher"),
    ("Meryem Kadiri", "meryem", "teacher"),
    ("Anas Ziani", "anas", "teacher"),
    ("Soukaina Filali", "soukaina", "teacher"),
    ("Bilal Tahiri", "bilal", "admin"),
    ("Kawtar Saidi", "kawtar", "admin"),
    ("Ayoub Naciri", "ayoub", "admin"),
]

def sql_escape(value: str) -> str:
    return value.replace("'", "''")

sql_lines = [
    "-- Correction des mots de passe des 20 utilisateurs de test",
    "BEGIN;",
    "",
]

for full_name, first_name, role in users:
    email = f"{first_name}@gmail.com"
    password = f"{first_name}123"
    hashed_password = password_hasher.hash(password)

    sql_lines.append(
        "UPDATE public.users SET "
        f"hashed_password = '{sql_escape(hashed_password)}', "
        "is_active = TRUE, "
        "is_deleted = FALSE, "
        "deleted_at = NULL, "
        "deleted_by = NULL "
        f"WHERE LOWER(email) = LOWER('{sql_escape(email)}');"
    )

sql_lines.extend([
    "",
    "COMMIT;",
    "",
])

output_file = "fix_test_users.sql"

with open(output_file, "w", encoding="utf-8") as file:
    file.write("\n".join(sql_lines))

print(f"Fichier SQL créé : {output_file}")
print(f"Hashes générés : {len(users)}")
print("Étape suivante : exécuter ce fichier dans pgAdmin.")
