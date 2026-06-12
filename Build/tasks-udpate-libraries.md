# Library Upgrade Review

Pragmatic review of the dependency list for PyBloom. The goal here is not to chase the newest version of everything blindly, but to identify which upgrades are worthwhile, which dependencies are probably unnecessary, and which changes are likely to create avoidable churn.

---

## 1. Bugs

The current dependency set is old. The main risk is not a single broken package, but an overly optimistic upgrade plan that assumes everything will work unchanged.

What looks sensible:

- upgrade the core Flask stack together
- upgrade requests/urllib3 together
- keep the rest simple unless the code actually needs changes

What I would not claim:

- that all upgrades are guaranteed to be code-change free
- that version pins can be replaced without testing
- that every transitive dependency should be treated as a first-class project dependency

---

## 2. Cleanup

### 2.1 Core web stack
✅ DONE

**Libraries:** `Flask`, `Werkzeug`, `Jinja2`, `click`, `itsdangerous`, `MarkupSafe`

These are tied together. Upgrading one usually implies upgrading the others to a compatible set.

**Recommendation:**
- upgrade them together
- test the app after the upgrade
- do not try to upgrade Flask in isolation

This is the main compatibility cluster in the project.

---

### 2.2 HTTP stack
✅ DONE

**Libraries:** `requests`, `urllib3`, `certifi`, `idna`

These should move together as well.

**Recommendation:**
- upgrade `requests` and `urllib3` as a pair
- let the supporting libraries follow the compatible versions pulled in by the resolver

This is the part most likely to affect network code indirectly, so it should be verified rather than assumed.

---

### 2.3 Scheduler and timezone support
✅ DONE

**Libraries:** `APScheduler`, `tzlocal`, `pytz`

The current code uses a simple background scheduler. This is not a complicated scheduler setup, so the upgrade risk is moderate.

**Recommendation:**
- upgrade `APScheduler`
- keep `pytz` only if the current scheduler/runtime still needs it
- do not introduce timezone refactors just for the sake of it

---

## 3. Nice-to-have

These are probably straightforward upgrades, but they should still be validated in the app:

- `pygal`
- `pyowm`
- `qhue`
- `rgbxy`
- `python-dateutil`

**Recommendation:** Upgrade them as part of the same dependency refresh, then run the app and a small manual smoke test:
- fetch weather
- write a database row
- render the graphs
- talk to the Hue bridge if you have it available

---

### 3.2 Dependencies That Look Unnecessary
✅ DONE


### 3.2.1 `geojson`

This dependency does not appear to be used by the codebase.

**Recommendation:** Remove it unless you know it is needed for something outside the current source tree.

---

### 3.2.2 `six`

This is a Python 2 compatibility layer. The project targets modern Python.

**Recommendation:** Remove it if nothing imports it directly or indirectly for a reason you care about.

---

### 3.2.3 `chardet`

The project does not use `chardet` directly. In modern `requests` setups it is often no longer the default charset detector anyway.

**Recommendation:** Remove it unless the resolver or another package specifically requires it.

---

### 3.2.4 `pysocks`

This may still be pulled in transitively by something else, but it is not obviously used in the application code.

**Recommendation:** Keep only if the dependency resolver or runtime actually needs it.

---

## 4. What The Upgrade Plan Should Actually Say

The current document claims that no code changes are needed across the entire upgrade. That is too strong.

More realistic wording:

- many of these upgrades will probably work without source changes
- some combinations may require small fixes once tested
- the only honest way to know is to upgrade in a branch and run the app

This is especially true because the current dependency versions are quite old.

---

## 5. Practical Upgrade Order

If you want to do this without making the repo unstable, use this order:

1. Upgrade the core Flask stack together
2. Upgrade `requests` and `urllib3`
3. Upgrade `APScheduler`
4. Upgrade the project-specific libraries
5. Remove unused dependencies
6. Run the app and confirm graphs, DB writes, and Hue actions still work

That sequence limits the blast radius if something breaks.

---

## 6. Files To Update

### `pyproject.toml`

Update dependency pins there first, because that is the actual project source of truth if `uv` is the main workflow.

### `requirements.txt`

Only keep this file if you actually need it for deployment or compatibility reasons. If you do keep it, regenerate it from the same dependency set so it does not drift.

---

## 7. Bottom Line

The original library review was directionally fine, but it overstated how safe the upgrades are.

The practical version is:

- upgrade the dependency groups together
- remove the obvious dead weight
- test the app after each meaningful step
- do not assume everything is source-compatible just because it is within the same major line
