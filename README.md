# 🎓 Smart University Assistant
### Assistant universitaire intelligent — Université Cadi Ayyad (UCA)

**Smart University Assistant** est une application intelligente conçue pour faciliter l'accès aux informations universitaires de l'Université Cadi Ayyad (UCA). Elle centralise les informations utiles aux étudiants et propose une interface conversationnelle capable de répondre aux questions en s'appuyant sur des documents universitaires grâce au **Retrieval-Augmented Generation (RAG)**.

Le projet combine le développement d'API, la gestion de données relationnelles, l'intelligence artificielle générative et l'automatisation des workflows.

---

## ✨ Fonctionnalités

- 🔐 **Authentification et gestion des utilisateurs** : inscription, connexion et contrôle d'accès selon les rôles.
- 🎓 **Informations universitaires** : accès aux informations concernant les établissements, les admissions et les services universitaires disponibles dans les données de l'application.
- 💬 **Assistant conversationnel IA** : interaction en langage naturel pour poser des questions sur l'université.
- 📚 **Recherche documentaire intelligente (RAG)** : récupération de passages pertinents dans les documents indexés pour contextualiser les réponses.
- 📄 **Gestion documentaire** : importation et traitement de documents pris en charge par l'application.
- 🧠 **Modèle de langage local** : génération de réponses à l'aide d'Ollama et du modèle configuré.
- 🗃️ **Base de données relationnelle** : stockage des données applicatives avec PostgreSQL.
- 🔎 **Recherche vectorielle** : indexation et recherche sémantique à l'aide de ChromaDB.
- ⚙️ **Automatisation des workflows** : intégration prévue avec n8n pour automatiser certains processus.
- 🛠️ **Interface d'administration** : gestion des utilisateurs et des fonctionnalités accessibles aux administrateurs.

## 🧰 Technologies utilisées

| Technologie | Rôle |
|---|---|
| Python | Langage principal |
| FastAPI | Backend et API REST |
| Streamlit | Interface utilisateur |
| PostgreSQL | Base de données relationnelle |
| SQLAlchemy | Accès aux données et ORM |
| ChromaDB | Stockage et recherche vectorielle |
| Ollama | Exécution locale du modèle de langage |
| Qwen 2.5 | Modèle de langage configuré pour le chatbot |
| Embeddings | Représentation vectorielle des textes |
| n8n | Automatisation des workflows |
| Git & GitHub | Gestion de versions et collaboration |

## 🏗️ Architecture

```text
                    ┌─────────────────────────┐
                    │    Interface Streamlit  │
                    │    Utilisateur / Admin  │
                    └────────────┬────────────┘
                                 │ HTTP / REST
                    ┌────────────▼────────────┐
                    │       FastAPI           │
                    │ Authentification, API,  │
                    │ logique métier          │
                    └──────┬──────────┬───────┘
                           │          │
                 ┌─────────▼───┐  ┌───▼─────────────┐
                 │ PostgreSQL  │  │ Service RAG     │
                 │ Données     │  │ Embeddings      │
                 │ applicatives│  │ Recherche       │
                 └─────────────┘  └───┬─────────────┘
                                      │
                             ┌────────▼────────┐
                             │    ChromaDB     │
                             │ Index vectoriel │
                             └─────────────────┘
                                      │
                             ┌────────▼────────┐
                             │     Ollama      │
                             │ Modèle Qwen 2.5 │
                             └─────────────────┘

                    n8n : automatisations des workflows
```

## 📂 Structure du projet

```text
Smart-University-Assistant/
│
├── backend/
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   └── config.py
│   └── services/
│       └── rag/
│           ├── rag_service.py
│           └── vector_store.py
│
├── frontend/
│   ├── assets/
│   │   └── uca_logo.png
│   └── app.py
│
├── data/
│   └── uca/
│       └── uca_seed_data.json
│
├── scripts/
│   └── index_uca_establishments.py
│
├── storage/
│   └── rag/
│       └── chroma/          # Données locales, non versionnées
│
├── .gitignore
├── README.md
└── requirements.txt
```

*Cette arborescence présente les principaux éléments du projet ; les autres modules et fichiers de configuration peuvent varier selon la version.*

## ⚙️ Prérequis

Avant de démarrer, installe les outils suivants :

- Python 3.11 ou une version compatible avec les dépendances du projet.
- PostgreSQL.
- Ollama.
- Git.
- n8n, si tu souhaites activer les automatisations.

Vérifie les installations :

```powershell
python --version
git --version
ollama --version
```

## 🚀 Installation

### 1. Cloner le dépôt

```powershell
git clone https://github.com/Ettayeb03/Smart-University-Assistant.git
cd Smart-University-Assistant
```

### 2. Créer l'environnement virtuel

Sous Windows PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloque l'activation, utilise temporairement :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Crée un fichier `.env` à la racine du projet et renseigne les paramètres correspondant à ta configuration locale.

Exemple indicatif :

```env
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/smart_university
OLLAMA_BASE_URL=http://localhost:11434
```

### 5. Préparer PostgreSQL

Crée la base de données PostgreSQL utilisée par l'application. Configure ensuite l'URL de connexion et applique, si nécessaire, les migrations ou la procédure d'initialisation prévue dans le projet.

### 6. Démarrer Ollama

Lance Ollama et télécharge le modèle si nécessaire :

```powershell
ollama pull qwen2.5:3b
```

Vérifie que le modèle est disponible :

```powershell
ollama list
```

Le nom du modèle doit correspondre à celui configuré dans le service RAG.

### 7. Initialiser les données universitaires

Vérifie les fichiers de données présents dans `data/uca/`. Si le script d'indexation des établissements est disponible et que les services nécessaires sont configurés, lance :

```powershell
python scripts/index_uca_establishments.py
```

Ce script prépare l'index vectoriel des informations sur les établissements de l'UCA. Exécute-le dans l'environnement Python du projet.

## ▶️ Lancement de l'application

Ouvre deux terminaux PowerShell dans le dossier du projet et active l'environnement virtuel dans chacun.

**Terminal 1 — Backend FastAPI**

```powershell
python -m uvicorn backend.main:app --reload
```

API : `http://127.0.0.1:8000`

Documentation interactive : `http://127.0.0.1:8000/docs`

**Terminal 2 — Interface Streamlit**

```powershell
streamlit run frontend/app.py
```

Streamlit affiche l'adresse locale de l'interface dans le terminal, généralement `http://localhost:8501`.

> Si le point d'entrée, les variables d'environnement ou les commandes diffèrent dans ta version du dépôt, adapte ces instructions aux fichiers réellement présents.

## 🧠 Fonctionnement du RAG

Le système RAG permet au chatbot de formuler des réponses à partir d'informations récupérées dans les documents indexés.

1. **Préparation des documents** : les contenus universitaires sont chargés et traités.
2. **Découpage** : les textes sont divisés en passages plus petits.
3. **Vectorisation** : les passages sont transformés en embeddings.
4. **Indexation** : les vecteurs et leurs métadonnées sont stockés dans ChromaDB.
5. **Recherche sémantique** : la question de l'utilisateur est vectorisée et les passages pertinents sont récupérés.
6. **Génération** : les passages récupérés servent de contexte au modèle de langage exécuté avec Ollama.
7. **Réponse** : le chatbot fournit une réponse contextualisée à l'utilisateur.

La qualité des réponses dépend de la pertinence des documents indexés et des passages retrouvés. Comme tout système génératif, le chatbot peut produire des réponses incomplètes ou incorrectes ; les informations importantes doivent être vérifiées auprès des sources universitaires officielles.

## 🔒 Sécurité et bonnes pratiques

- Ne publie jamais le fichier `.env`, les secrets ou les identifiants de connexion.
- N'ajoute pas `.venv/` au dépôt.
- Garde les données locales générées par ChromaDB hors du contrôle de version.
- Vérifie les autorisations d'accès aux endpoints d'administration.
- Évite d'exposer publiquement une instance de développement FastAPI avec `--reload`.
- Protège les données personnelles et les documents importés.

## 🛣️ Améliorations envisagées

- Amélioration de la précision des réponses du chatbot.
- Ajout de citations et de liens vers les sources universitaires.
- Extension des données sur les établissements, les admissions et les services étudiants.
- Automatisation de tâches avec n8n.
- Ajout de tests automatisés pour le backend et le pipeline RAG.
- Amélioration du suivi des conversations et de l'expérience utilisateur.
- Déploiement sur une infrastructure adaptée.

## 🎯 Objectifs pédagogiques

Ce projet permet de mettre en pratique :

- Le développement d'API REST avec FastAPI.
- La conception d'une application Python modulaire.
- La gestion de données avec PostgreSQL et SQLAlchemy.
- L'intégration d'un LLM et d'un pipeline RAG.
- La recherche sémantique avec une base vectorielle.
- La création d'une interface avec Streamlit.
- La gestion de versions avec Git et GitHub.
- L'intégration de workflows d'automatisation.

## 👨‍💻 Auteur

**Ettayeb Benchekroune**

Étudiant en ingénierie informatique — Data Science & Intelligence Artificielle.

Projet académique : **Smart University Assistant — Assistant universitaire intelligent**.
