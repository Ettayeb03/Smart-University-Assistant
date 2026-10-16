
from pathlib import Path
import os

import pymupdf
import pytesseract
from PIL import Image
from pypdf import PdfReader

from backend.core.config import settings


class DocumentExtractionError(Exception):
    """Erreur lors de l'extraction du texte d'un document."""


# Chemins Windows et modèles OCR
TESSERACT_EXE = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TESSDATA_DIR = PROJECT_ROOT / "models" / "tessdata"

if TESSERACT_EXE.is_file():
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_EXE)


def _extract_pdf_page_with_ocr(
    pdf_document: pymupdf.Document,
    page_index: int,
) -> str:
    """Convertit une page PDF en image et applique l'OCR."""
    page = pdf_document.load_page(page_index)

    # Résolution suffisante pour la reconnaissance de texte
    pixmap = page.get_pixmap(
        matrix=pymupdf.Matrix(2, 2),
        alpha=False,
    )

    image = Image.frombytes(
        "RGB",
        [pixmap.width, pixmap.height],
        pixmap.samples,
    )

    try:
        return pytesseract.image_to_string(
            image,
            lang="fra+eng+ara",
            config=f'--tessdata-dir "{TESSDATA_DIR}"',
        ).strip()
    except Exception as exc:
        raise DocumentExtractionError(
            f"Échec de l'OCR à la page {page_index + 1}."
        ) from exc


def extract_text_from_file(file_path: str | Path) -> str:
    """
    Extrait le texte d'un fichier PDF ou TXT.
    Utilise l'OCR pour les pages PDF sans texte extractible.
    """
    path = Path(file_path)

    if not path.is_file():
        raise DocumentExtractionError("Le fichier est introuvable.")

    extension = path.suffix.lower()

    try:
        if extension == ".txt":
            text = path.read_text(encoding="utf-8-sig")

        elif extension == ".pdf":
            reader = PdfReader(str(path))

            if reader.is_encrypted:
                raise DocumentExtractionError(
                    "Les PDF protégés par mot de passe ne sont pas pris en charge."
                )

            # Ouvre le PDF avec PyMuPDF pour permettre le rendu des pages
            with pymupdf.open(str(path)) as pdf_document:
                if len(reader.pages) != len(pdf_document):
                    raise DocumentExtractionError(
                        "Impossible de lire toutes les pages du PDF."
                    )

                pages_text = []

                for page_index, page in enumerate(reader.pages):
                    page_text = (page.extract_text() or "").strip()

                    # L'OCR est utilisé uniquement si le texte est absent
                    if len(page_text) < 20:
                        page_text = _extract_pdf_page_with_ocr(
                            pdf_document,
                            page_index,
                        )

                    if page_text:
                        pages_text.append(
                            f"[Page {page_index + 1}]\n{page_text}"
                        )

                text = "\n\n".join(pages_text)

        else:
            raise DocumentExtractionError(
                "Format non pris en charge. Utilisez PDF ou TXT."
            )

    except DocumentExtractionError:
        raise
    except Exception as exc:
        raise DocumentExtractionError(
            "Impossible d'extraire le texte de ce fichier."
        ) from exc

    text = text.replace("\x00", "").strip()

    if not text:
        raise DocumentExtractionError(
            "Aucun texte extractible. Vérifiez la qualité du document "
            "et la présence des modèles OCR."
        )

    return text
