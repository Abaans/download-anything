"""Validate portable skill packages without running their workflows."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit
import yaml


def validate_skill(root):
    root = Path(root).resolve()
    errors = []
    def fail(message):
        errors.append(f"{root.name}: {message}")
    for p in root.rglob("*"):
        if p.is_symlink():
            fail(f"symlinks are not portable: {p.relative_to(root)}")
    source = root / "SKILL.md"
    if not source.is_file():
        return errors + [f"{root.name}: missing SKILL.md"]
    text = source.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    try:
        front = yaml.safe_load(match.group(1)) if match else None
        if not isinstance(front, dict):
            raise ValueError("missing YAML mapping")
        name = front.get("name", "")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            fail("invalid skill name")
        elif name != root.name:
            fail("frontmatter name differs from folder")
        description = front.get("description")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            fail("description must be 1–1024 characters")
    except (ValueError, yaml.YAMLError) as exc:
        fail(f"invalid frontmatter: {exc}")
    try:
        metadata = yaml.safe_load((root / "agents/openai.yaml").read_text(encoding="utf-8"))
        interface = metadata["interface"]
        if not isinstance(interface, dict):
            raise TypeError("interface must be a mapping")
        if not isinstance(interface.get("display_name"), str) or not interface["display_name"].strip():
            fail("missing display name")
        short = interface.get("short_description", "")
        if not isinstance(short, str) or not 25 <= len(short) <= 64:
            fail("short description must be 25–64 characters")
        if "$" + root.name not in interface.get("default_prompt", ""):
            fail("default prompt must invoke this skill")
    except (OSError, TypeError, KeyError, yaml.YAMLError) as exc:
        fail(f"invalid agent metadata: {exc}")
    if not (root / "LICENSE").is_file():
        fail("missing installed-copy license")
    errors.extend(validate_links(root, root))
    return errors


def validate_links(directory, boundary):
    errors = []
    boundary = Path(boundary).resolve()
    for source in Path(directory).rglob("*.md"):
        if ".git" in source.parts:
            continue
        text = source.read_text(encoding="utf-8")
        targets = re.findall(r"\[[^\]]*\]\(([^)]+)\)", text)
        targets += re.findall(r'\b(?:src|href)="([^"]+)"', text)
        for raw in targets:
            target = raw.strip().strip("<>")
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            resolved = (source.parent / unquote(url.path)).resolve()
            if not resolved.is_relative_to(boundary):
                errors.append(f"{source.name}: resource escapes package: {target}")
            elif not resolved.exists():
                errors.append(f"{source.name}: missing resource: {target}")
    return errors


def validate_repository(root):
    root = Path(root).resolve()
    errors = []
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    if not skills:
        errors.append("No skills found")
    for source in skills:
        errors.extend(validate_skill(source.parent))
    errors.extend(validate_links(root, root))
    try:
        catalog = json.loads((root / "skills.json").read_text())
        catalog_names = {skill["name"] for skill in catalog["skills"]}
        if catalog_names != {source.parent.name for source in skills}:
            errors.append("Catalog must list every bundled skill exactly once")
        if len(catalog_names) != len(catalog["skills"]):
            errors.append("Duplicate catalog entry")
        for entry in catalog["skills"]:
            for field in ("entrypoint", "readme", "image"):
                target = (root / entry[field]).resolve()
                if not target.is_relative_to(root) or not target.is_file():
                    errors.append(f"Invalid catalog resource: {entry['name']}/{field}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"Invalid catalog: {exc}")
    for p in root.rglob("*"):
        if ".git" in p.parts or ".venv" in p.parts:
            continue
        if p.is_symlink():
            errors.append(f"Symlink in release: {p.relative_to(root)}")
        if p.name in {".DS_Store", ".env"} or p.suffix in {".part", ".aria2"}:
            errors.append(f"Runtime artifact: {p.relative_to(root)}")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate_repository(args.root)
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print("PASS: skill metadata, installed resources, licenses and repository links")
