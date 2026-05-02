# Exercice 2 — Injection de noms + comparaison MLFlow

## Objectif

Modifier le chunker pour inclure le nom du Pokémon dans chaque chunk,
régénérer les embeddings, relancer l'évaluation, et comparer les deux
runs dans MLFlow.

---

## Tâche 1 — injection de noms (`python/students/rag-loader/`)

```bash
cd python/students/rag-loader
just install-dev
just test -v   # 5 tests échouent — c'est normal
```

### Ce que vous devez ajouter

**`rag_loader/task_inputs.py`** — un nouveau champ :

```python
inject_document_name: bool = Field(
    default=False,
    description="If True, prepend 'Pokémon: {name}' to each chunk's content",
)
```

**`rag_loader/app.py`** — utiliser le champ dans la boucle de chunking.
La fonction `_extract_pokemon_name` est déjà présente dans le fichier.
Remplacer `final_content = content` par la logique conditionnelle.

Vérifier :

```bash
just test -v   # tous les tests doivent passer
```

---

## Tâche 2 — générer les nouveaux chunks

Une fois les tests au vert, générer les chunks avec injection dans un
répertoire séparé (sans toucher aux chunks baseline) :

```bash
uv run rag_loader/main.py \
  --inject_document_name True \
  --output_dir ../../data/chunks-name-injection
```

---

## Tâche 3 — recharger pgvector

Le formateur effectue ces commandes pour vider la base et charger les
nouveaux embeddings :

```bash
# Vider la table
docker exec rag-postgres psql -U rag -d rag -c "TRUNCATE document_chunks;"

# Recharger avec les chunks enrichis
cd python/rag-embedder
uv run main --input_dir ../../data/chunks-name-injection \
            --output_dir ../../data/embeddings-name-injection
```

---

## Tâche 4 — évaluer la nouvelle configuration

Depuis `python/students/eval-retriever` :

```bash
uv run eval_retriever/main.py --approach_tag "name-injection"
```

---

## Tâche 5 — comparer dans MLFlow

Ouvrir **http://localhost:5000** → expérience `rag-retrieval-comparison`.

Vous devez voir deux runs : `baseline` et `name-injection`.

1. Cochez les deux runs
2. Cliquez sur **Compare**
3. Observez l'évolution de `recall_at_1`, `recall_at_3`, `recall_at_5` et `mrr`

**Question** : quelle métrique progresse le plus ? Pourquoi l'injection du nom
aide-t-elle particulièrement les requêtes du type "Qui est Pikachu ?" ?
