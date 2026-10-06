# Evidence Lab — E000, Day 1

We take one accepted CaSiNo negotiation, independently reconstruct its allocation
and scores, and verify that we understand the source correctly.

We have **not** performed the complete E000 audit, calculated Pareto dominance
across accepted deals, analyzed dialogue language, trained an ML model, or built
an API, database, or frontend.

## Start here

For a beginner's explanation of every function and statement, follow the
[line-by-line walkthrough with flowcharts](docs/WALKTHROUGH.md).
Before the batch-audit milestone, follow the
[first VS Code debugger session](docs/DEBUGGER_FIRST_SESSION.md) to place red-dot
breakpoints, inspect intermediate data, and compare it with expected values.
The [input contract](sources/casino.input.md) shows the raw JSON fields, including
`chat_logs`; `schema.py` defines the converted output structure.

Open a terminal in this repository. On this machine:

```bash
cd /home/mastii/Desktop/hustle/evidence-lab
uv sync --locked
uv run --locked pytest
uv run --locked ruff check .
uv run --locked ruff format --check .
```

The public GitHub repository is
[`SrivastavaHarsit/evidence-lab`](https://github.com/SrivastavaHarsit/evidence-lab).
You can copy it onto another machine with:

```bash
git clone https://github.com/SrivastavaHarsit/evidence-lab.git
cd evidence-lab
```

Then use the same setup and check commands above.

`uv sync --locked` creates `.venv`, a private Python environment for this project,
and installs the versions in `uv.lock`. `uv run` uses that environment; no manual
activation is needed. The first sync needs internet access for tools. The tests
themselves use only tiny local examples and never download data. Pytest runs the
tests; Ruff checks code mistakes and formatting.

uv is installed on this machine. If a new terminal cannot find it, run
`source "$HOME/.local/bin/env"`. On another Linux/macOS machine, install it using
the [official uv instructions](https://docs.astral.sh/uv/getting-started/installation/):

```bash
curl -LsSf https://astral.sh/uv/0.12.23/install.sh | sh
source "$HOME/.local/bin/env"
```

Python 3.12 is selected by `.python-version`; uv can obtain it when absent.

## Optional: check one record from the full source

From the repository folder:

```bash
uv run --locked python scripts/download_casino.py
uv run --locked python scripts/check_one.py data/raw/casino.json
```

The first command downloads only the revision in
[`sources/casino.manifest.json`](sources/casino.manifest.json), checks its SHA256
(a fingerprint of the exact bytes) and size, then saves it under `data/raw/`.
A mismatch raises an error before replacing any existing dataset. A local
`casino.retrieval.json` records when and what was downloaded. Both files are
ignored by Git. The second command takes an explicit local path and reads it;
it does not download or independently check the file's checksum.

Selection is the first accepted deal in file order. The pinned file selects
dialogue **0**, with **mturk_agent_2** as proposer. Expected results:

| Participant | Food, water, firewood received | Points per unit in that order | Computed = recorded |
| --- | --- | --- | --- |
| mturk_agent_1 | 1, 0, 3 | 4, 3, 5 | 19 |
| mturk_agent_2 | 2, 3, 0 | 3, 4, 5 | 18 |

For participant 1, `1 × 4 + 0 × 3 + 3 × 5 = 19`. Each resource totals three units
across the two people. High, Medium, and Low preferences mean 5, 4, and 3 points
per unit, respectively ([CaSiNo paper, section 2](https://aclanthology.org/2021.naacl-main.254.pdf)).

## Follow the data

```text
CaSiNo JSON
    ↓
casino.py
    ↓
validated Python record
    ↓
score reconstruction
    ↓
comparison with recorded score
    ↓
pass / visible failure
```

A parser translates raw JSON dictionaries into named Python records. Here those
records are dataclasses: small containers with named fields. `frozen=True`
prevents accidentally changing their fields. Type hints describe expected
types; the parser performs the actual validation. Direct dataclass construction
does not validate data, so external source data must go through the parser.

| Raw field | Meaning |
| --- | --- |
| `dialogue_id` | Identity of this dialogue. |
| `participant_info.mturk_agent_1` / `mturk_agent_2` | The two fixed participant roles, scoped to this dialogue. |
| Each participant's `value2issue` | Which resource has High, Medium, or Low value. |
| Final `Submit-Deal.id` | Who proposed the accepted offer. |
| Submission's `task_data.issue2youget` | Quantities for the proposer. |
| Submission's `task_data.issue2theyget` | Quantities for the other participant. |
| Final `Accept-Deal.id` | The other participant, accepting that offer. |
| Each participant's `outcomes.points_scored` | Recorded score to compare against our calculation. |

`participant_1` always means `mturk_agent_1`, and `participant_2` always means
`mturk_agent_2`; these never switch when the proposer changes. The parser checks
the final submission/acceptance pair, integer quantities from 0 to 3, resource
conservation, complete preferences, and both scores. Missing values, including
`None`, are errors. Walkaways are passed over because there is no accepted deal;
an invalid accepted record stops processing. Records after the selected deal
and unrelated source fields are not audited.

## Study the files in this order

1. This README: run the example and understand its output.
2. `src/evidence_lab/negotiation/schema.py`: the containers and arithmetic.
3. `tests/fixtures/casino_dialogue_0.json`: the small real input; read its neighboring README for origin and omissions.
4. `tests/test_casino.py`: the expected results and examples of rejected input.
5. `src/evidence_lab/negotiation/casino.py`: follow the translation step by step.
6. `scripts/check_one.py`, then `scripts/download_casino.py`: starting the check and acquiring bytes.
7. `sources/casino.manifest.json`, then `docs/STATUS.md` and `docs/DECISIONS.md`: source identity, progress, and choices.
8. `pyproject.toml`, `.python-version`, `.gitignore`, and `.github/workflows/checks.yml`: packaging, tools, and automated checks.
9. Glance at `uv.lock`: generated exact tool versions; you do not need to memorize it. The two `__init__.py` files mark Python packages.

## Inspect Git

Git records snapshots of files. The original version is saved in the commit
tagged `baseline-before-milestone-1`. That tag preserves the files as they were
before repository documentation and formatting cleanup. It has 21 passing
tests and a known Ruff spacing issue in two import comments. The original
workflow also references an unavailable `setup-uv` action version. Later commits
on `main` fix the formatting and action reference without changing program
behavior.

Follow the [Git workflow guide](docs/GIT_WORKFLOW.md) to save future changes,
start milestone 1 on a branch, and inspect the original version.

```bash
git branch --show-current        # current branch
git status --short              # changed and new files
git log --oneline --decorate --all  # saved history and baseline tag
git diff                        # changes to already tracked, unstaged files
git ls-files --others --exclude-standard  # new files not yet tracked
git diff --cached               # changes staged for the next commit
git status --short --ignored    # also show ignored paths, marked !!
git check-ignore -v data/raw/casino.json   # the rule keeping raw data out
```

When you have reviewed your next changes and want to save a snapshot:

```bash
git add .
git diff --cached --stat
git commit -m "Describe the changes you made"
git push
```

`git add` stages files (selects them for the next snapshot); `.gitignore` keeps
raw data and the environment out. `git commit` saves the staged snapshot locally;
`git push` uploads committed changes to GitHub after a remote is connected.

Source attribution and the upstream CC BY 4.0 license are recorded in the
[manifest](sources/casino.manifest.json) and [fixture notes](tests/fixtures/README.md).

## Visual map: follow every function and its input/output

Open the **[complete visual flow map](docs/FLOW_MAP.html)** in a browser for
rendered diagrams with zoom and full-screen controls. Its editable source is
[FLOW_MAP.md](docs/FLOW_MAP.md).

Start with **map 2: who calls whom**, then **map 4: the order in which the deal is
built**. Maps 5–8 expand every parser/scoring helper. The remaining maps cover
data contracts, downloading, tests, and supporting tools.
