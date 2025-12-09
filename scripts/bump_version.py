
import os
import re
import sys

# Files to update
FILES_TO_BUMP = [
    "README.md",
    "app.py",
    "src/agent.py",
    "src/monitoring.py",
    "src/data_loader.py",
    "CHANGELOG.md"
]

# Regex patterns for different file types
# Matches: v14.0, V14.0, Version: 14.0, etc.
# We are looking for "vX.Y" or "VX.Y" followed by standard delimiters
VERSION_PATTERN = r"(v|V)(\d+)\.(\d+)(-Optimized|-RAG)?"

def get_current_version():
    """Reads the current version from README.md as the source of truth."""
    if not os.path.exists("README.md"):
        print("❌ README.md not found.")
        sys.exit(1)
        
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
        
    match = re.search(VERSION_PATTERN, content)
    if match:
        major = int(match.group(2))
        minor = int(match.group(3))
        tag = match.group(4) or ""
        return major, minor, tag
    
    return None

def bump_version(major, minor, tag):
    """Increments the version (Patch/Minor level strategy)."""
    # Strategy: Always increment minor for 'push' events
    new_minor = minor + 1
    new_version_str = f"v{major}.{new_minor}{tag}"
    nice_version_str = f"V{major}.{new_minor}{tag}" # Uppercase V for some displays
    return major, new_minor, tag, new_version_str, nice_version_str

def update_file(filepath, current_major, current_minor, new_major, new_minor, tag):
    """Replaces version strings in a file."""
    if not os.path.exists(filepath):
        print(f"⚠️ File not found: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Pattern to find the EXACT current version to replace it safely
    # We look for v14.0 or V14.0
    current_pattern = f"(v|V){current_major}\.{current_minor}{tag}"
    
    # Replacement function to keep the case (v or V)
    def replace_callback(match):
        prefix = match.group(1)
        return f"{prefix}{new_major}.{new_minor}{tag}"

    new_content = re.sub(current_pattern, replace_callback, content)
    
    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ Updated {filepath} -> v{new_major}.{new_minor}{tag}")
    else:
        print(f"ℹ️ No version match in {filepath}")

def main():
    print("🔄 Starting Auto-Version Bump...")
    current = get_current_version()
    if not current:
        print("❌ Could not detect current version in README.md")
        sys.exit(1)
        
    major, minor, tag = current
    print(f"ℹ️ Current Version: v{major}.{minor}{tag}")
    
    new_major, new_minor, tag, new_v_str, nice_v_str = bump_version(major, minor, tag)
    print(f"🚀 New Version: {new_v_str}")
    
    # Update all files
    for f in FILES_TO_BUMP:
        update_file(f, major, minor, new_major, new_minor, tag)
        
    # Append to CHANGELOG if strictly creating a new entry (Optional, simplistic here)
    # Ideally, we would prepend a new header. For now, we update references.
    
    # Set Output for GitHub Actions
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as gh_out:
            gh_out.write(f"NEW_VERSION={new_v_str}\n")

if __name__ == "__main__":
    main()
