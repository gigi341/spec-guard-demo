from github import Github

def post_pr_comment(findings, repo_name, pr_number, gh_token):
    g    = Github(gh_token)
    repo = g.get_repo(repo_name)
    pr   = repo.get_pull(pr_number)

    if not findings:
        body = "## ✅ Spec Integrity Check\nNo contradictions found."
    else:
        body = f"## ⚠️ Spec Integrity Check — {len(findings)} finding(s)\n\n"
        for f in findings:
            icon = {"critical":"🔴","warning":"🟡","info":"🔵"}.get(f["severity"],"⚪")
            body += f"---\n### {icon} {f['severity'].upper()}\n"
            body += f"**Doc claim ({f['doc_file']}):** {f['doc_claim']}\n\n"
            body += f"**Code:** `{f['code_file']}` line {f['code_line']}\n\n"
            body += f"**Explanation:** {f['explanation']}\n\n"
        body += "\n*Powered by IBM Bob — spec-guard*"

    marker = "Spec Integrity Check"
    for c in pr.get_issue_comments():
        if marker in c.body:
            c.edit(body)
            print("  Updated existing comment.")
            return
    pr.create_issue_comment(body)
    print("  Posted new comment.")