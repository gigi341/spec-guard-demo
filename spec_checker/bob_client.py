import subprocess
import json
import os
import shutil

def build_prompt(changed_files: list[dict], docs: list[dict]) -> str:
    doc_text = ""
    for d in docs:
        doc_text += f"\n### {d['filename']}\n{d['content']}\n"

    diff_text = ""
    for f in changed_files:
        diff_text += f"\n### {f['filename']} ({f['status']})\n{f['patch']}\n"

    return f"""You have full repository context. Use your understanding of all files and call chains.

=== DOCUMENTATION CLAIMS ===
{doc_text}

=== PULL REQUEST DIFF ===
{diff_text}

=== TASK ===
Find every contradiction between the documentation claims and the changed code.

You MUST respond with ONLY a JSON array. No thinking tags, no explanation, no markdown.
Start your response with [ and end with ].

Each item must have exactly:
{{"severity": "critical" or "warning" or "info", "doc_claim": "exact sentence from docs", "doc_file": "e.g. README.md", "code_file": "e.g. src/user.py", "code_line": <integer>, "explanation": "reference other affected files if relevant"}}

If no contradictions: respond with exactly: []"""


def call_bob(prompt: str) -> list[dict]:
    print("  Calling Bob Shell (non-interactive)...")

    bob_path = shutil.which("bob")
    if not bob_path:
        bob_path = r"C:\Users\Pc Planet\AppData\Roaming\npm\bob.cmd"

    if not shutil.which("bob") and not os.path.exists(bob_path):
        print("  Bob not found on this system — falling back to mock.")
        return call_bob_mock()

    with open("bob_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    result = subprocess.run(
        [bob_path, "--approval-mode", "yolo",
         "--chat-mode", "ask", "--output-format", "json"],
        input=prompt,
        capture_output=True, text=True, timeout=180, cwd=os.getcwd()
    )

    raw = result.stdout.strip()
    print(f"  Bob exit code: {result.returncode}")
    print(f"  Full Bob output:\n{raw[:800]}")

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
        text = parsed.get("result") or parsed.get("content") or raw
        if isinstance(text, list):
            return text
    except json.JSONDecodeError:
        text = raw

    if "<thinking>" in text and "</thinking>" in text:
        text = text[text.rfind("</thinking>") + len("</thinking>"):]
    text = text.strip()

    start = text.find("[")
    end   = text.rfind("]") + 1
    if start == -1 or end == 0:
        print("  No JSON array found.")
        return []

    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        print("  JSON parse failed.")
        return []


def call_bob_mock() -> list[dict]:
    try:
        with open("findings.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []