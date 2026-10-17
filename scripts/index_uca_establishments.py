import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.rag.rag_service import RAGService

JSON_PATH = PROJECT_ROOT / "data" / "uca" / "uca_seed_data.json"

OVERVIEW_ID = -999999
OVERVIEW_FILENAME = "uca_liste_etablissements.txt"


def main():
    with JSON_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    establishments = data.get("establishments", [])
    if not establishments:
        raise ValueError("Aucun établissement trouvé dans le JSON.")

    service = RAGService()
    before = service.vector_store.count()

    # Document synthétique : noms, sigles et villes.
    grouped = {}
    for item in establishments:
        city = item.get("city", "Ville inconnue")
        grouped.setdefault(city, []).append(
            f"{item.get('name', 'Nom inconnu')} "
            f"({item.get('short_name', 'sigle non renseigné')})"
        )

    overview_lines = [
        "Liste officielle des établissements de l'Université Cadi Ayyad (UCA).",
        f"L'UCA compte {len(establishments)} établissements dans ce jeu de données.",
        "Question : Quels sont les établissements de l'UCA ?",
        "Pour répondre, présenter les noms des établissements et leurs sigles.",
        "",
    ]

    for city, names in grouped.items():
        overview_lines.append(f"Établissements de {city} :")
        overview_lines.extend(f"- {name}" for name in names)
        overview_lines.append("")

    overview_text = "\n".join(overview_lines)

    overview_chunks = service.index_document(
        document_id=OVERVIEW_ID,
        filename=OVERVIEW_FILENAME,
        text=overview_text,
    )

    # Une fiche distincte par établissement.
    total_chunks = overview_chunks

    for index, item in enumerate(establishments, start=1):
        name = item.get("name", "Nom inconnu")
        sigle = item.get("short_name", "")
        city = item.get("city", "Ville inconnue")

        lines = [
            "Fiche établissement de l'Université Cadi Ayyad (UCA).",
            f"Nom : {name}.",
            f"Sigle : {sigle}.",
            f"Ville : {city}.",
        ]

        if item.get("address"):
            lines.append(f"Adresse : {item['address']}.")
        if item.get("phones"):
            lines.append(f"Téléphones : {', '.join(item['phones'])}.")
        if item.get("email"):
            lines.append(f"Email : {item['email']}.")
        if item.get("website"):
            lines.append(f"Site web : {item['website']}.")

        chunks = service.index_document(
            document_id=-100000 - index,
            filename=f"UCA - {sigle or index} - {city}.txt",
            text="\n".join(lines),
        )
        total_chunks += chunks

    after = service.vector_store.count()

    print(f"Établissements traités : {len(establishments)}")
    print(f"Passages indexés pendant cette exécution : {total_chunks}")
    print(f"Passages avant : {before}")
    print(f"Passages après : {after}")
    print("Les documents existants non liés à ces identifiants sont conservés.")


if __name__ == "__main__":
    main()
