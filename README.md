# Projet — TenyGuard

## 1. Présentation

**TenyGuard** est une application d'intelligence artificielle basée sur la Programmation Orientée Objet (POO) destinée à détecter automatiquement les gros mots, insultes et expressions vulgaires en **langue malagasy** dans des vidéos.

L'application prend une vidéo en entrée, extrait sa piste audio, transforme la parole en texte grâce à un système de Speech-to-Text, puis analyse la transcription afin d'identifier les propos vulgaires ou offensants.

Le système conserve également les **timestamps** des détections afin de savoir précisément à quel moment de la vidéo un gros mot a été prononcé.

L'objectif est de construire une solution spécialisée dans la langue malagasy, capable de gérer les différentes variantes d'écriture, les expressions, le contexte et les formulations volontairement modifiées.

---

## 2. Fonctionnement général

Le pipeline principal sera :

```text
                    ┌─────────────┐
                    │    Vidéo    │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    FFmpeg   │
                    │ Extraction  │
                    │    audio    │
                    └──────┬──────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Speech-to-Text  │
                  │ Malagasy / mg   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Transcription │
                  │ + timestamps   │
                  └────────┬────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       ┌──────────────┐          ┌──────────────┐
       │ Dictionnaire │          │     LLM      │
       │ de termes    │          │ Analyse du   │
       │ vulgaires    │          │ contexte     │
       └──────┬───────┘          └──────┬───────┘
              │                         │
              └────────────┬────────────┘
                           ▼
                  ┌─────────────────┐
                  │ Classification  │
                  │ / Détection     │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │    Résultats    │
                  │ mot + timestamp │
                  │ + confiance     │
                  └─────────────────┘
```

---

## 3. Stack technique

Le langage principal du projet est **Python**, structuré en **Programmation Orientée Objet (POO)**.

Technologies utilisées :

* **Python 3.10+** : Langage principal
* **FastAPI** : Framework API REST haute performance
* **Pydantic** : Validation des données et schémas
* **SQLAlchemy & PostgreSQL** : ORM et base de données relationnelle principale
* **FFmpeg** : Extraction et traitement des fichiers audio/vidéo
* **Speech-to-Text** : Modèle de transcription de parole en malagasy
* **LLM** : Analyse contextuelle et classification des termes ambigus
* **pytest** : Tests unitaires et d'intégration

---

## 4. Architecture logicielle

Le projet respecte une architecture modulaire et orientée objet (POO) :

```text
tenyguard/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── health.py
│   │       ├── videos.py
│   │       └── detection.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── models/
│   │   ├── video.py
│   │   ├── transcription.py
│   │   └── detection.py
│   │
│   ├── services/
│   │   ├── video_service.py
│   │   ├── audio_service.py
│   │   ├── transcription_service.py
│   │   ├── profanity_service.py
│   │   └── llm_service.py
│   │
│   ├── detectors/
│   │   ├── base.py
│   │   ├── dictionary_detector.py
│   │   ├── context_detector.py
│   │   └── hybrid_detector.py
│   │
│   └── database/
│       ├── connection.py
│       └── repositories/
│
├── tests/
│   ├── conftest.py
│   └── test_health.py
│
├── data/
│   ├── videos/
│   ├── audio/
│   └── datasets/
│
├── scripts/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 5. Installation et Démarrage Local (sans Docker)

### 1. Cloner le projet et créer un environnement virtuel

```bash
python -m venv venv
# Sur Windows:
venv\Scripts\activate
# Sur Linux/macOS:
source venv/bin/activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configurer l'environnement

```bash
cp .env.example .env
```

### 4. Lancer l'application FastAPI

```bash
uvicorn app.main:app --reload
```

L'API sera accessible sur `http://127.0.0.1:8000`.
La documentation interactive OpenAPI / Swagger est disponible sur `http://127.0.0.1:8000/docs`.

### 5. Exécuter les tests

```bash
pytest
```

---

## 6. Pipeline CI/CD GitHub Actions

Un workflow GitHub Actions est configuré dans `.github/workflows/ci.yml`.

À chaque `push` ou `pull_request` sur les branches `main`, `master` ou `develop`, le pipeline :
1. Déploie un conteneur de service **PostgreSQL 15** ;
2. Configure **Python 3.11** et installe les dépendances ;
3. Effectue la vérification syntaxique du code ;
4. Exécute la suite de tests automatisés avec **pytest**.

## 7. Système de détection Hybride (POO)

Le système de détection repose sur une hiérarchie de classes POO dérivant de `BaseProfanityDetector` :

1. **Niveau 1 — Dictionnaire (`DictionaryDetector`)** : Base de termes vulgaires malagasy et correspondances.
2. **Niveau 2 — Normalisation** : Nettoyage du texte (casse, accents, répétitions).
3. **Niveau 3 — Analyse contextuelle (`ContextDetector`)** : Appel LLM pour lever les ambiguïtés contextuelles.
4. **Niveau 4 — Détecteur Hybride (`HybridDetector`)** : Combinaison des règles dictionnaire et de l'analyse LLM pour produire un score final de confiance.

---

## 8. Structure du résultat de détection

Exemple d'output JSON retourné par l'API :

```json
{
  "detections": [
    {
      "text": "expression détectée",
      "start_time": 92.4,
      "end_time": 93.1,
      "category": "insult",
      "severity": "high",
      "confidence": 0.94
    }
  ]
}
```