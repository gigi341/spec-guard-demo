import os, sys, json
from diff_extractor import get_pr_diff
from doc_reader import get_docs
from bob_client import build_prompt, call_bob, call_bob_mock
from github_poster import post_pr_comment

def main():
    use_mock = "--mock" in sys.argv

    pr_number = int(os.environ.get("PR_NUMBER", "1"))
    repo_name = os.environ.get("REPO_NAME")
    gh_token  = os.environ.get("GH_TOKEN")

    print(f"Repo: {repo_name} | PR: {pr_number} | Mock: {use_mock}")

    print("\n[M2] Extracting diff...")
    changed_files = get_pr_diff(repo_name, pr_number, gh_token)

    print("\n[M3] Reading docs...")
    docs = get_docs(".")

    if use_mock:
        print("\n[M4] Using mock Bob output (no coins spent)")
        findings = call_bob_mock()
    else:
        print("\n[M4] Calling IBM Bob Shell...")
        prompt = build_prompt(changed_files, docs)
        findings = call_bob(prompt)

    print(f"\n[Result] {len(findings)} finding(s)")
    print(json.dumps(findings, indent=2))

    with open("findings.json", "w") as f:
        json.dump(findings, f, indent=2)
    print("findings.json written.")
    
    print("\n[M5] Posting PR comment...")
    post_pr_comment(findings, repo_name, pr_number, gh_token)

if __name__ == "__main__":
    main()