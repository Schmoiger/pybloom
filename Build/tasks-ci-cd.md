# CI/CD Pipeline for PyBloom

## Context

PyBloom runs on a **Raspberry Pi on the local network**, not in the cloud. The development laptop and the Pi are on the same network. Code is deployed by transferring files from the laptop to the Pi. There is no cloud hosting, no Docker, and no Kubernetes.

The goal is a **simplified CI/CD pipeline** that:

- **CI (Continuous Integration):** Validates code quality on every push using GitHub Actions
- **CD (Continuous Deployment):** Deploys validated code to the Raspberry Pi via a local script

---

## 1. Current Deployment Workflow

Today, deployment is manual:

1. Edit code on the Mac laptop
2. Transfer files to the Pi (scp / rsync / copy)
3. SSH into the Pi and restart the app

This is fragile and error-prone. There's no automated testing, no linting, and no verification that the code works before it arrives on the Pi.

---

## 2. Proposed CI/CD Architecture

```
┌─────────────┐     push      ┌──────────────────┐
│  Mac Laptop │ ─────────────►│  GitHub Actions  │
│  (dev env)  │               │  (CI pipeline)   │
└──────┬──────┘               └──────────────────┘
       │                              │
       │                        pass/fail status
       │                              │
       ▼                              ▼
┌─────────────┐   make deploy  ┌──────────────────┐
│  Mac Laptop │ ─────────────►│  Raspberry Pi    │
│  (dev env)  │   rsync + SSH │  (production)    │
└─────────────┘               └──────────────────┘
```

**Key design decisions:**

- **CI runs in the cloud** (GitHub Actions) — tests and linting don't need the Pi
- **CD runs locally** (from the laptop) — because the Pi is on a private network with no inbound access
- **No self-hosted runner on the Pi** — overkill for this project; adds maintenance burden
- **No cloud deployment** — the Pi IS the production environment

---

## 3. CI Pipeline (GitHub Actions)

### What CI checks

| Check | Tool | Purpose |
|-------|------|---------|
| Unit tests | `pytest` | Verify code logic works |
| Linting | `ruff` | Catch style errors and common mistakes |
| Type checking | `mypy` (optional) | Catch type errors |

### GitHub Actions workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.14"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --dev

      - name: Lint with ruff
        run: uv run ruff check .

      - name: Run tests
        run: uv run pytest --tb=short

      - name: Type check with mypy
        run: uv run mypy --ignore-missing-imports pybloom.py db_utils.py app/
        continue-on-error: true  # advisory for now, not blocking
```

### What CI does NOT do

- **Does not deploy** — deployment is a separate, manual step from the laptop
- **Does not access the Pi** — the Pi is on a private network
- **Does not run integration tests** — those require the Pi's hardware (Hue bridge, OWM API key)

### CI status badge

Add to `README.md`:

```markdown
[![CI](https://github.com/Schmoiger/pybloom/actions/workflows/ci.yml/badge.svg)](https://github.com/Schmoiger/pybloom/actions/workflows/ci.yml)
```

---

## 4. CD Pipeline (Local Deployment Script)

### Approach: Makefile + rsync + SSH

A `Makefile` in the project root provides a `deploy` target that:

1. Runs tests locally (fast check before deploying)
2. Syncs code to the Pi via `rsync`
3. Restarts the app service on the Pi via `ssh`

### Makefile

Create `Makefile`:

```makefile
# =============================================================================
# PyBloom Deployment
# =============================================================================
# Usage:
#   make deploy          — deploy to production Pi
#   make deploy-dry      — preview what would be transferred
#   make status          — check if the app is running on the Pi
# =============================================================================

# Configuration — adjust these to match your setup
PI_HOST        ?= raspberrypi.local
PI_USER        ?= pi
PI_PROJECT_DIR ?= ~/Projects/pybloom
LOCAL_PROJECT_DIR = .

# rsync exclusions — files that should NOT be deployed
RSYNC_EXCLUDES = \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.DS_Store' \
  --exclude='credentials.*' \
  --exclude='.env' \
  --exclude='.env.*' \
  --exclude='database.sqlite3' \
  --exclude='*.svg' \
  --exclude='pybloomweather*.json' \
  --exclude='uv.lock' \
  --exclude='Build/' \
  --exclude='docs/' \
  --exclude='tests/' \
  --exclude='.github/'

# Deploy to the Raspberry Pi
.PHONY: deploy
deploy: check-env
	@echo "==> Running tests locally first..."
	uv run pytest --tb=short -q
	@echo ""
	@echo "==> Syncing code to $(PI_USER)@$(PI_HOST):$(PI_PROJECT_DIR)..."
	rsync -avz --delete \
		$(RSYNC_EXCLUDES) \
		$(LOCAL_PROJECT_DIR)/ \
		$(PI_USER)@$(PI_HOST):$(PI_PROJECT_DIR)/
	@echo ""
	@echo "==> Installing/updating dependencies on Pi..."
	ssh $(PI_USER)@$(PI_HOST) "cd $(PI_PROJECT_DIR) && uv sync --no-dev"
	@echo ""
	@echo "==> Restarting PyBloom service on Pi..."
	ssh $(PI_USER)@$(PI_HOST) "sudo systemctl restart pybloom"
	@echo ""
	@echo "==> Checking service status..."
	ssh $(PI_USER)@$(PI_HOST) "sudo systemctl status pybloom --no-pager" || true
	@echo ""
	@echo "==> Deployment complete!"

# Preview what would be transferred (dry run)
.PHONY: deploy-dry
deploy-dry: check-env
	rsync -avz --delete --dry-run \
		$(RSYNC_EXCLUDES) \
		$(LOCAL_PROJECT_DIR)/ \
		$(PI_USER)@$(PI_HOST):$(PI_PROJECT_DIR)/

# Check if the app is running on the Pi
.PHONY: status
status: check-env
	@echo "==> Service status:"
	ssh $(PI_USER)@$(PI_HOST) "sudo systemctl status pybloom --no-pager" || true
	@echo ""
	@echo "==> Recent logs:"
	ssh $(PI_USER)@$(PI_HOST) "sudo journalctl -u pybloom --no-pager -n 20"

# View live logs from the Pi
.PHONY: logs
logs: check-env
	ssh $(PI_USER)@$(PI_HOST) "sudo journalctl -u pybloom -f"

# Validate environment variables are set
.PHONY: check-env
check-env:
	@if [ -z "$(PI_HOST)" ]; then echo "ERROR: PI_HOST not set"; exit 1; fi
```

### Deployment exclusions explained

The rsync exclusions ensure these files are **never deployed** (they either don't belong on the Pi, or the Pi has its own copy):

| Excluded | Reason |
|----------|--------|
| `.git/` | No need for version history on production |
| `.venv/` | Pi has its own virtual environment |
| `__pycache__/` | Compiled bytecode — regenerated on Pi |
| `credentials.*` | Secrets — Pi has its own copy |
| `.env`, `.env.*` | Secrets — Pi has its own copy |
| `database.sqlite3` | Pi has its own production database |
| `*.svg` | Generated graphs — regenerated on Pi at runtime |
| `Build/`, `docs/`, `tests/` | Development-only files |
| `.github/` | CI configuration — not needed on Pi |
| `uv.lock` | Lockfile — `uv sync` resolves on Pi |

---

## 5. Systemd Service on the Pi

For the `make deploy` script to restart the app, PyBloom needs to run as a systemd service on the Pi.

### Service file: `/etc/systemd/system/pybloom.service`

```ini
[Unit]
Description=PyBloom Weather Station
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Projects/pybloom
ExecStart=/home/pi/Projects/pybloom/.venv/bin/flask run --host=0.0.0.0
Restart=on-failure
RestartSec=10

# Environment
Environment=FLASK_APP=app.py
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
```

### One-time setup on the Pi

```bash
# Install uv on the Pi (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repo (or copy it initially)
cd ~/Projects
git clone https://github.com/Schmoiger/pybloom.git
cd pybloom

# Set up the virtual environment
uv sync --no-dev

# Create the systemd service
sudo cp /path/to/pybloom.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pybloom
sudo systemctl start pybloom

# Verify
sudo systemctl status pybloom
```

### Alternative: screen/tmux session

If you prefer not to use systemd, you can run the app in a `screen` or `tmux` session:

```bash
# Start a named screen session
screen -S pybloom

# Inside the screen session
cd ~/Projects/pybloom
uv run flask run --host=0.0.0.0

# Detach: Ctrl+A, D
# Reattach: screen -r pybloom
```

In this case, the Makefile's deploy target would restart by sending a command to the screen session:

```makefile
restart-screen:
	ssh $(PI_USER)@$(PI_HOST) \
		"screen -S pybloom -X stuff 'C-c' && sleep 1 && \
		 screen -S pybloom -X stuff 'uv run flask run --host=0.0.0.0\n'"
```

---

## 6. Pre-commit Hooks (Optional, Local)

For faster feedback, add a pre-commit hook that runs linting before each commit:

### Install pre-commit

```bash
# Add to pyproject.toml optional dependencies
# dev = ["pytest", "pytest-cov", "ruff", "pre-commit"]

uv run pre-commit install
```

### Create `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

This catches formatting and lint issues before they reach GitHub, giving you instant feedback locally.

---

## 7. Deployment Checklist

### First-time setup (Pi)

- [ ] Install Python 3.14+ on the Pi
- [ ] Install `uv` on the Pi
- [ ] Clone/copy the repo to `~/Projects/pybloom`
- [ ] Create `credentials.py` on the Pi with API keys
- [ ] Run `uv sync --no-dev` to create the virtual environment
- [ ] Verify the app starts: `uv run flask run --host=0.0.0.0`
- [ ] Set up the systemd service
- [ ] Set up SSH key authentication from laptop to Pi

### First-time setup (Laptop / GitHub)

- [ ] Add `pytest`, `ruff` to `pyproject.toml` dev dependencies
- [ ] Create `.github/workflows/ci.yml`
- [ ] Create `Makefile`
- [ ] Create `.pre-commit-config.yaml` (optional)
- [ ] Push to GitHub — verify CI passes

### Ongoing workflow

1. Make changes on the laptop
2. `git add` and `git commit` — pre-commit hooks run linting
3. `git push` — GitHub Actions runs CI
4. Verify CI passes on GitHub
5. `make deploy` — deploys to the Pi
6. `make status` — verify the service is running

---

## 8. Future Improvements

These are optional enhancements for when the project grows:

### SSH key authentication

Set up passwordless SSH from the laptop to the Pi so the deploy script doesn't prompt for a password:

```bash
# On the laptop
ssh-keygen -t ed25519 -C "pybloom-deploy"
ssh-copy-id pi@raspberrypi.local

# Test
ssh pi@raspberrypi.local "echo ok"
```

### Git tag-based deployment

Tag a release before deploying:

```bash
git tag v0.2.0
git push origin v0.2.0
make deploy
```

This creates a record of what version is running on the Pi.

### Deploy with confirmation prompt

Add a safety check to the Makefile:

```makefile
deploy: check-env
	@read -p "Deploy to production Pi? [y/N] " confirm; \
	if [ "$$confirm" != "y" ]; then echo "Aborted."; exit 1; fi
	# ... rest of deploy
```

### Health check after deploy

Add a curl-based health check:

```makefile
health-check:
	@echo "==> Checking if PyBloom is responding..."
	@curl -sf http://$(PI_HOST):5000/ > /dev/null && \
		echo "PyBloom is running!" || \
		echo "ERROR: PyBloom is not responding on port 5000"
```

### Self-hosted GitHub Actions runner (not recommended)

It IS possible to run a GitHub Actions self-hosted runner on the Pi, which would let GitHub Actions deploy directly. However, this is not recommended for this project because:

- The Pi would need to be always on and internet-accessible
- It adds security surface (the Pi becomes a CI runner)
- It requires maintaining the runner software
- The Makefile approach is simpler and more appropriate for a single-device deployment

---

## 9. Summary

| Component | Where it runs | What it does |
|-----------|---------------|--------------|
| **CI** (GitHub Actions) | GitHub cloud | Tests, linting on every push/PR |
| **CD** (Makefile) | Laptop → Pi via SSH/rsync | Deploy code, install deps, restart service |
| **Pre-commit** (optional) | Laptop (local) | Lint before commit |
| **systemd** | Raspberry Pi | Keep the app running as a service |

### Files to create

| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | CI pipeline definition |
| `Makefile` | Deploy commands |
| `.pre-commit-config.yaml` | Local pre-commit hooks |
| `/etc/systemd/system/pybloom.service` | Pi service file (created once) |

### Commands

| Command | What it does |
|---------|-------------|
| `make deploy` | Deploy to the Pi (runs tests first) |
| `make deploy-dry` | Preview what would be transferred |
| `make status` | Check if the app is running on the Pi |
| `make logs` | View live logs from the Pi |