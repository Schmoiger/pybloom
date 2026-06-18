# CI/CD Pipeline for PyBloom

Pragmatic CI/CD plan for a home project running on a Raspberry Pi on the local network. The goal is to get useful automation without turning this into a production platform.

---

## 1. Bugs

PyBloom is not cloud-hosted. It runs on a Pi, and deployment happens from the development laptop over the local network.

There is nothing in the current plan that looks like a hard blocker. The main risks are implementation mistakes rather than a broken deployment model.

The few concrete things to watch are:

- making sure the CI workflow matches the actual Python and dependency setup
- making sure the deploy script does not sync secrets or generated files by accident
- making sure the service definition matches how the app is actually started

---

## 2. Cleanup

That means the sensible split is:

- **CI**: run tests and linting on GitHub Actions
- **CD**: deploy from the laptop to the Pi with a local script

What I would not add yet:

- Docker
- Kubernetes
- a self-hosted GitHub Actions runner on the Pi
- a full release pipeline with approvals, environments, and tags

Those are reasonable in larger projects, but they add more maintenance than value here.

---

## 3. Cleanup

Today the workflow is basically manual:

1. Edit code on the laptop
2. Copy files to the Pi
3. SSH into the Pi and restart the app

That works, but it is easy to miss a broken test or a bad deploy.

---

## 4. Cleanup

### Recommended scope

Keep CI small:

- `pytest`
- `ruff`
- optional `mypy` if you want extra static checking

That is enough to catch the obvious problems without overloading the setup.

### Suggested GitHub Actions workflow

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
```

### Notes

- I would not make `mypy` blocking unless you actually start using type hints consistently.
- I would not add integration tests to CI yet, because the Hue bridge and Pi-specific setup make that brittle.
- A status badge in `README.md` is fine, but it is optional.

---

## 5. Cleanup

### Recommended approach

Use a small `Makefile` that:

1. Runs tests locally before deployment
2. Syncs the project to the Pi with `rsync`
3. Restarts the service on the Pi over SSH

That is enough for this project.

### Suggested Makefile shape

Create `Makefile`:

```makefile
PI_HOST ?= raspberrypi.local
PI_USER ?= pi
PI_PROJECT_DIR ?= ~/Projects/pybloom

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
  --exclude='Build/' \
  --exclude='docs/' \
  --exclude='tests/' \
  --exclude='.github/'

.PHONY: deploy
deploy:
	uv run pytest --tb=short -q
	rsync -avz --delete \
		$(RSYNC_EXCLUDES) \
		./ \
		$(PI_USER)@$(PI_HOST):$(PI_PROJECT_DIR)/
	ssh $(PI_USER)@$(PI_HOST) "cd $(PI_PROJECT_DIR) && uv sync --no-dev"
	ssh $(PI_USER)@$(PI_HOST) "sudo systemctl restart pybloom"

.PHONY: status
status:
	ssh $(PI_USER)@$(PI_HOST) "sudo systemctl status pybloom --no-pager" || true

.PHONY: logs
logs:
	ssh $(PI_USER)@$(PI_HOST) "sudo journalctl -u pybloom --no-pager -n 20"
```

### What I would keep out

I would not add a lot of extra Makefile targets yet.

Not needed right now:

- `deploy-dry`
- confirmation prompts
- tag-based deployment
- automatic health checks after deploy
- screen/tmux restart logic

Those are all defensible, but they are not necessary for the first useful version.

---

## 6. Cleanup

PyBloom should run as a `systemd` service on the Pi. That is the simplest reliable way to keep it alive after reboot and restart it after deployment.

### Service file

Create `/etc/systemd/system/pybloom.service` on the Pi:

```ini
[Unit]
Description=PyBloom Weather Station
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Projects/pybloom
ExecStart=/home/pi/Projects/pybloom/.venv/bin/python -m flask --app app run --host=0.0.0.0
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### One-time setup

- Install `uv` on the Pi
- Copy or clone the repo to the Pi
- Create the Pi’s credentials/configuration
- Run `uv sync --no-dev`
- Enable the `systemd` service
- Set up SSH key access from laptop to Pi

I would not add a `screen` or `tmux` fallback unless you specifically prefer that workflow.

---

## 7. Nice-to-have

These are reasonable later, but not required now:

- pre-commit hooks for local linting
- a simple health endpoint
- a deploy confirmation prompt
- a post-deploy `curl` check
- Git tags for releases

If you want one extra beyond CI and deploy, I would pick pre-commit hooks first, because they are cheap and improve feedback speed.

---

## 8. Practical Recommendation

If you want the minimum useful CI/CD setup, do this:

1. Add a GitHub Actions workflow for `pytest` and `ruff`
2. Add a `Makefile` with `deploy`, `status`, and `logs`
3. Run PyBloom as a `systemd` service on the Pi

That gets you the most value for the least complexity.
