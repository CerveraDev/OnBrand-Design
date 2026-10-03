from __future__ import annotations

import os
from pathlib import Path
import re

from .contract import ROOT, project_contract, read_json


def installation_files(project: str, platform: str, workspace: Path, root: Path = ROOT):
    if platform not in ("codex", "claude"):
        raise ValueError("Only Codex and Claude have skill installations")
    project_contract(project, root)
    metadata = read_json(root / "projects" / project / "project.json")
    skills = metadata["skills"]
    files = {}
    for kind, name in skills.items():
        if name != f"onbrand-{project}-{kind}" or len(name) > 64 or not re.fullmatch(r"[a-z0-9-]+", name):
            raise ValueError("Project skill ID is not collision-safe")
        source = root / "projects" / project / "skills" / name / "SKILL.md"
        if not source.is_file():
            raise ValueError(f"Canonical skill missing: {name}")
        folder = workspace / (".agents" if platform == "codex" else ".claude") / "skills" / name
        relative_root = Path(os.path.relpath(root, workspace)).as_posix()
        reference = Path(os.path.relpath(source, folder)).as_posix()
        manual = "disable-model-invocation: true\n" if platform == "claude" else ""
        token = "$" if platform == "codex" else "/"
        files[folder / "SKILL.md"] = (
            f"---\nname: {name}\ndescription: Explicitly invoked OnBrand {project} {kind} workflow.\n"
            f"{manual}---\n\n# {name}\n\n"
            f"Run only after a HUMAN explicitly invokes {token}{name}. Ordinary topic matches are not invocation.\n\n"
            f"Read [the canonical workflow]({reference}); resolve its references from its own folder. "
            "Do not copy project rules or approve inputs on behalf of the user.\n\n"
            f"The core repository is at `{relative_root}` relative to this workspace. "
            "Run commands from that core root, using Python 3.10+ with the standard library.\n\n"
            "For an approved campaign request file, use the shared dispatcher:\n\n"
            f"```bash\npython3 -m tools.platform_adapters.cli build --platform {platform} "
            "--request <request.json> --output <output-folder> --explicit\n```\n\n"
            "Use `emit` instead of `build` to validate and emit canonical JSON without downloading assets. "
            "Image work follows the canonical image skill; this adapter does not provide an image generator. "
            "Do not invoke another skill automatically. If shell execution is unavailable, "
            "provide the same command for the human; never bypass QA or reconstruct a package manually.\n"
        )
        if platform == "codex":
            files[folder / "agents/openai.yaml"] = (
                f'interface:\n  display_name: "{name}"\n'
                f'  short_description: "Explicit OnBrand {project} {kind} workflow"\n'
                'policy:\n  allow_implicit_invocation: false\n'
            )
    return files


def install(project: str, platform: str, workspace: Path, root: Path = ROOT):
    files = installation_files(project, platform, workspace.resolve(), root.resolve())
    # Refuse collisions before writing any file; installation never edits host settings.
    for path, content in files.items():
        if path.exists() and path.read_text(encoding="utf-8") != content:
            raise ValueError(f"Refusing to overwrite an existing adapter: {path}")
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return sorted(str(path) for path in files)
