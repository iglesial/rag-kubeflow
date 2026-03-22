# Guide d'installation — Pré-requis

> A effectuer **avant** la première séance. Comptez 30-45 minutes.

## 1. Docker Desktop

Télécharger et installer Docker Desktop :
- **Windows** : https://docs.docker.com/desktop/install/windows-install/
- **macOS** : https://docs.docker.com/desktop/install/mac-install/
- **Linux** : https://docs.docker.com/desktop/install/linux/

Vérifier :

```bash
docker --version        # Docker version 27.x ou plus récent
docker compose version  # Docker Compose version v2.x
```

> **Windows** : activer WSL 2 si ce n'est pas déjà fait. Docker Desktop le propose à l'installation.

## 2. Python 3.13+

Installer Python 3.13 ou plus récent :
- **Windows** : https://www.python.org/downloads/ (cocher "Add to PATH")
- **macOS** : `brew install python@3.13`
- **Linux** : `sudo apt install python3.13` ou via pyenv

Vérifier :

```bash
python --version   # Python 3.13.x
```

## 3. uv (gestionnaire de paquets Python)

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Vérifier :

```bash
uv --version   # uv 0.6.x ou plus récent
```

## 4. kind (Kubernetes in Docker)

```bash
# Windows (PowerShell)
choco install kind
# ou télécharger depuis https://kind.sigs.k8s.io/docs/user/quick-start/#installation

# macOS
brew install kind

# Linux
go install sigs.k8s.io/kind@latest
# ou télécharger le binaire
```

Vérifier :

```bash
kind --version   # kind v0.25.x ou plus récent
```

## 5. kubectl

```bash
# Windows (PowerShell)
choco install kubernetes-cli

# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/
```

Vérifier :

```bash
kubectl version --client   # Client Version: v1.31.x ou plus récent
```

## 6. Git + compte GitHub

Git est probablement déjà installé. Sinon :
- **Windows** : https://git-scm.com/download/win
- **macOS** : `xcode-select --install`
- **Linux** : `sudo apt install git`

Vérifier :

```bash
git --version   # git version 2.x
```

Vous aurez besoin d'un **compte GitHub** pour forker le repository template.

## 7. just (task runner)

```bash
# Windows (PowerShell)
choco install just
# ou : cargo install just

# macOS
brew install just

# Linux
cargo install just
# ou via les packages de votre distribution
```

Vérifier :

```bash
just --version   # just 1.x
```

## 8. VS Code (recommandé)

Télécharger : https://code.visualstudio.com/

Extensions recommandées :
- **Python** (Microsoft)
- **Ruff** (Astral Software)
- **Even Better TOML** (tamasfe)

## Checklist finale

Exécuter ces commandes pour vérifier que tout est prêt :

```bash
docker --version          # ✓
python --version          # ✓ >= 3.13
uv --version              # ✓
kind --version            # ✓
kubectl version --client  # ✓
git --version             # ✓
just --version            # ✓
```

## Premier lancement (en séance)

Le jour de la première séance, vous ferez :

```bash
# 1. Cloner le repository
git clone https://github.com/<org>/rag-kubeflow-starter.git
cd rag-kubeflow-starter

# 2. Démarrer PostgreSQL
docker compose up -d

# 3. Installer les dépendances du premier package
cd python/rag-loader
just install-dev

# 4. Lancer les tests (ils échoueront — c'est normal !)
just test
```

> **Attention** : le premier `just install-dev` téléchargera le modèle d'embedding (`all-MiniLM-L6-v2`, ~80 Mo). Prévoyez une connexion internet.
