
import os
import re
import sys
import subprocess

FILES_TO_BUMP = [
    "README.md",
    "app.py",
    "src/agent.py",
    "src/monitoring.py",
    "src/data_loader.py",
    "CHANGELOG.md"
]

VERSION_PATTERN = r"(v|V)(\d+)\.(\d+)(-Optimized|-RAG)?"

# Keywords that trigger a MAJOR bump (V15.0 -> V16.0)
MAJOR_KEYWORDS = ["feat", "feature", "new", "major", "breaking", "release", "ajout"]

def get_last_commit_message():
    try:
        msg = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], encoding="utf-8")
        return msg.strip().lower()
    except:
        return ""

def get_current_version():
    if not os.path.exists("README.md"): return None
    with open("README.md", "r", encoding="utf-8") as f: content = f.read()
    match = re.search(VERSION_PATTERN, content)
    if match:
        return int(match.group(2)), int(match.group(3)), match.group(4) or ""
    return None

def determine_bump_type(commit_msg):
    # Check for keywords indicating a feature/major update
    for kw in MAJOR_KEYWORDS:
        if kw in commit_msg:
            return "major"
    return "minor"

def bump_version(major, minor, tag, bump_type):
    if bump_type == "major":
        new_major = major + 1
        new_minor = 0
    else:
        new_major = major
        new_minor = minor + 1
    return new_major, new_minor, tag

def update_file(filepath, current_major, current_minor, new_major, new_minor, tag):
    if not os.path.exists(filepath): return
    with open(filepath, "r", encoding="utf-8") as f: content = f.read()
    
    current_pattern = f"(v|V){current_major}\.{current_minor}{tag}"
    def replace_callback(match):
        prefix = match.group(1)
        return f"{prefix}{new_major}.{new_minor}{tag}"

    new_content = re.sub(current_pattern, replace_callback, content)
    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f: f.write(new_content)
        print(f"✅ Updated {filepath}")

def main():
    print("🔄 Auto-Heuristic Version Bump...")
    current = get_current_version()
    if not current: sys.exit(1)
    
    major, minor, tag = current
    commit_msg = get_last_commit_message()
    print(f"ℹ️ Analysis Commit: '{commit_msg}'")
    
    bump_type = determine_bump_type(commit_msg)
    print(f"ℹ️ Detected Type: {bump_type.upper()}")
    
    new_major, new_minor, tag = bump_version(major, minor, tag, bump_type)
    new_v_str = f"v{new_major}.{new_minor}{tag}"
    print(f"🚀 New Version: {new_v_str}")
    
    for f in FILES_TO_BUMP:
        update_file(f, major, minor, new_major, new_minor, tag)
        
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as gh_out:
            gh_out.write(f"NEW_VERSION={new_v_str}\n")

if __name__ == "__main__":
    main()
