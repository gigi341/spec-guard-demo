import os
from github import Github

def get_pr_diff(repo_name: str, pr_number: int, gh_token: str) -> list[dict]:
    """
    Pulls the diff for a PR and returns a list of changed files.
    Each item: { filename, patch, status }
    Filters to code files only — no lock files, no config noise.
    """
    g = Github(gh_token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    CODE_EXTENSIONS = {
        ".py", ".js", ".ts", ".jsx", ".tsx",
        ".go", ".java", ".rb", ".php", ".cs",
        ".cpp", ".c", ".h", ".rs", ".swift"
    }

    IGNORE_PATTERNS = [
        "package-lock.json", "yarn.lock", "poetry.lock",
        "Pipfile.lock", ".min.js", ".min.css"
    ]

    changed_files = []

    for f in pr.get_files():
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in CODE_EXTENSIONS:
            continue
        if any(pattern in f.filename for pattern in IGNORE_PATTERNS):
            continue
        if f.patch is None:
            continue

        changed_files.append({
            "filename": f.filename,
            "patch": f.patch,
            "status": f.status,       # added, modified, removed
            "additions": f.additions,
            "deletions": f.deletions,
        })

    print(f"  Found {len(changed_files)} changed code files in PR #{pr_number}")
    for cf in changed_files:
        print(f"    {cf['status']:8s}  {cf['filename']}")

    return changed_files


if __name__ == "__main__":
    repo_name = os.environ.get("REPO_NAME")
    pr_number = int(os.environ.get("PR_NUMBER", "1"))
    gh_token  = os.environ.get("GH_TOKEN")

    files = get_pr_diff(repo_name, pr_number, gh_token)
    print(f"\nDiff extractor done. {len(files)} files ready for Bob.")