import os
import json

def main():
    pr_number = os.environ.get("PR_NUMBER")
    repo_name = os.environ.get("REPO_NAME")
    bob_key   = os.environ.get("BOB_API_KEY")
    gh_token  = os.environ.get("GH_TOKEN")

    print(f"Spec checker starting...")
    print(f"Repo:      {repo_name}")
    print(f"PR number: {pr_number}")
    print(f"Bob key present: {bool(bob_key)}")
    print(f"GH token present: {bool(gh_token)}")

    findings = []

    with open("findings.json", "w") as f:
        json.dump(findings, f, indent=2)

    print("Stub complete. findings.json written.")

if __name__ == "__main__":
    main()