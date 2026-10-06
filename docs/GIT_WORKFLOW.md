# Save your work with Git and GitHub

Run these commands from `/home/mastii/Desktop/hustle/evidence-lab`.

The public GitHub repository is
[`SrivastavaHarsit/evidence-lab`](https://github.com/SrivastavaHarsit/evidence-lab),
with `main` and the baseline tag pushed. This local repository uses GitHub CLI
authentication as `SrivastavaHarsit` for future pushes.

## The saved starting point

`baseline-before-milestone-1` is an annotated tag pointing to the first commit.
It preserves the original project files, including the existing import-comment
spacing issue. A later maintenance commit updates the repository instructions
and fixes that formatting. Neither commit implements milestone 1.

A commit is a saved snapshot. A branch is a movable name for your line of work.
A tag names a particular snapshot; leave this baseline tag where it is.
GitHub is the remote copy of the commits you push.

The raw dataset, `.venv`, and caches stay on your machine and are ignored by Git.
The surrounding research-planning folder is outside this repository.
Commits use your GitHub noreply address, configured only for this repository.

## Start milestone 1

Create a branch once, before editing:

```bash
git switch main
git switch -c milestone-1
```

After making a useful set of changes:

```bash
git status
git diff
uv run --locked pytest
uv run --locked ruff check .
uv run --locked ruff format --check .
git add .
git diff --cached --stat
git diff --cached
git commit -m "Describe what changed"
git push -u origin milestone-1
```

Review the files before committing; exclude any credentials or private files.
`git add` selects changes, `git commit` saves them locally, and `git push`
uploads them. Saving a file in the editor does not perform these Git steps.
After the first push, use `git push` for later commits on that same branch.
Open a pull request from `milestone-1` to `main` on GitHub when it is ready.
After merging it, return locally with `git switch main` and `git pull --ff-only`.

## Inspect the original baseline

These commands do not change your working files:

```bash
git log --oneline --decorate --all
git show --stat baseline-before-milestone-1
git diff baseline-before-milestone-1 main
```

For a separate folder containing the original version:

```bash
git worktree add --detach ../evidence-lab-baseline baseline-before-milestone-1
```

This lets you inspect the baseline while continuing work in your main folder.
The baseline folder needs its own `uv sync --locked` to run tests.

## Check your GitHub connection

```bash
gh auth status
git remote -v
git status --short --branch
```

`origin` should point to `https://github.com/SrivastavaHarsit/evidence-lab.git`.
Authenticate as the repository owner before pushing. A clean Git status means
your local files match the current commit; it does not by itself prove that
the commit has been pushed.
