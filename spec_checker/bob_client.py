import subprocess
import json
import os

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

    # Write prompt to temp file to avoid shell escaping issues
    with open("bob_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    result = subprocess.run(
        [r"C:\Users\Pc Planet\AppData\Roaming\npm\bob.cmd",
         "--approval-mode", "yolo",
         "--chat-mode", "ask",
         "--output-format", "json"],
        input=prompt,
        capture_output=True, text=True, timeout=180, cwd=os.getcwd()
    )

    raw = result.stdout.strip()
    print(f"  Bob exit code: {result.returncode}")
    print(f"  Full Bob output:\n{raw[:800]}")

    # Parse structured JSON output from Bob
    # Bob --output-format json wraps response in {"type":"result","result":"..."}
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            # direct array
            return parsed
        # extract result field
        text = parsed.get("result") or parsed.get("content") or raw
        if isinstance(text, list):
            return text
    except json.JSONDecodeError:
        text = raw

    # Strip <thinking> if present
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
    return [
        {
            "severity": "critical",
            "doc_claim": "GET /users/:id returns 404 when a user is not found.",
            "doc_file": "README.md",
            "code_file": "src/user.py",
            "code_line": 12,
            "explanation": "The updated code raises a ValueError which results in a 500, not a 404 as documented. Any client catching 404 will miss this error."
        }
    ]