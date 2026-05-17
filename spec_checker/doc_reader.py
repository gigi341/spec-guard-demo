import os
import pathlib

def get_docs(repo_root: str = ".") -> list[dict]:
    """
    Reads documentation files from the repo.
    Returns list of { filename, content }
    """
    root = pathlib.Path(repo_root)
    docs = []

    TARGETS = [
        root / "README.md",
        root / "README.rst",
    ]
    DOC_DIRS = [
        root / "docs",
        root / "doc",
    ]
    OPENAPI_NAMES = [
        "openapi.yaml", "openapi.json",
        "swagger.yaml", "swagger.json"
    ]

    # README
    for target in TARGETS:
        if target.exists():
            content = target.read_text(encoding="utf-8", errors="ignore")
            docs.append({"filename": str(target), "content": content})
            print(f"  Read: {target} ({len(content)} chars)")

    # /docs folder
    for doc_dir in DOC_DIRS:
        if doc_dir.exists():
            for md_file in doc_dir.rglob("*.md"):
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                docs.append({"filename": str(md_file), "content": content})
                print(f"  Read: {md_file} ({len(content)} chars)")

    # OpenAPI anywhere in repo
    for openapi_name in OPENAPI_NAMES:
        for match in root.rglob(openapi_name):
            content = match.read_text(encoding="utf-8", errors="ignore")
            docs.append({"filename": str(match), "content": content})
            print(f"  Read: {match} ({len(content)} chars)")

    if not docs:
        print("  WARNING: No documentation files found.")

    print(f"  Total docs loaded: {len(docs)}")
    return docs


if __name__ == "__main__":
    docs = get_docs(".")
    for d in docs:
        print(f"\n--- {d['filename']} ---")
        print(d['content'][:300])
        print("...")