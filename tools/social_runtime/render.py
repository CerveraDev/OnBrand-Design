"""Render the slides of a built social package from the project's scaffold.

The package says what fills each slot; this step puts it there. Each slide's
scaffold frame is filled in Chromium by `render_slides.cjs` and exported at the
format's pixel size, then checked: output dimensions, file size, every image
loaded, and every text slot within its frame's line limit and inside the canvas.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from .crops import CropError, image_dimensions
from .formats import FORMATS_PATH, FormatError, load_formats, require_format
from .frames import FRAMES_FILE, FrameError, load_frames


ROOT = Path(__file__).resolve().parents[2]
RENDERER = Path(__file__).with_name("render_slides.cjs")
RENDER_REPORT = "render-report.json"
SLIDES_DIR = "slides"
JPEG_QUALITY = 92


class RenderError(ValueError):
    """Raised when a package cannot be rendered, with the specific reason."""


@dataclass(frozen=True)
class RenderResult:
    passed: bool
    slides: list[Path]
    report: Path
    zip_path: Path | None
    checks: list[dict]
    warnings: list[str]


def render_package(
    package_dir: Path | str,
    *,
    project_dir: Path | None = None,
    formats_path: Path = FORMATS_PATH,
    renderer=None,
) -> RenderResult:
    package_dir = Path(package_dir).resolve()
    try:
        package = json.loads((package_dir / "social-package.json").read_text(encoding="utf-8"))
        qa = json.loads((package_dir / "qa-report.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        raise RenderError(f"Not a built social package: {package_dir.name}") from err
    if not qa.get("passed"):
        raise RenderError("The package failed blocking QA; fix the build before rendering")
    project_dir = Path(project_dir) if project_dir else ROOT / "projects" / package["campaign"]["project"]
    scaffold_dir = project_dir / "social" / "scaffold"
    try:
        definitions = load_frames(project_dir / "social" / "templates" / FRAMES_FILE)
        fmt = require_format(load_formats(formats_path), package["composition"]["format"])
    except (FrameError, FormatError) as err:
        raise RenderError(str(err)) from err
    for name, key in (("scaffold.html", "scaffold_html_sha256"), ("scaffold.css", "scaffold_css_sha256")):
        path = scaffold_dir / name
        if not path.is_file():
            raise RenderError(f"The project scaffold is missing {name}")
        expected = definitions.get("generated_from", {}).get(key)
        if expected and hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RenderError(f"Frame definitions are out of date with {name}; regenerate them before rendering")
    frames = definitions["frames"]
    composition = package["composition"]

    warnings: list[str] = []
    jobs = []
    plan = []
    shutil.rmtree(package_dir / SLIDES_DIR, ignore_errors=True)
    for variant, content in sorted(package["variants"].items()):
        for slide in content["slides"]:
            frame = frames.get(slide["frame"])
            if frame is None:
                raise RenderError(f"Frame {slide['frame']} is not defined for this project")
            output = package_dir / SLIDES_DIR / variant / f"slide-{slide['index']:02d}.jpg"
            images = []
            for image in slide["images"]:
                src = image.get("src")
                if src is None:
                    src = image["source_src"]
                    warnings.append(
                        f"{variant} slide {slide['index']}: crop '{image['crop_id']}' is planned, "
                        f"so '{image['slot']}' is rendered from its uncropped source"
                    )
                elif not src.startswith(("https://", "http://")):
                    src = (package_dir / src).as_uri()
                images.append({"slot": image["slot"], "url": src})
            text = [
                {"slot": slot, "value": value, "italic_accent": frame["text_slots"][slot]["italic_accent"]}
                for slot, value in slide["text"].items()
            ]
            jobs.append({"output": str(output), "frame": slide["frame"], "images": images, "text": text})
            plan.append((f"{variant}:slide-{slide['index']}", output, frame, slide))
    scale = composition["width"] / next(iter(plan))[2]["canvas"]["width"]
    job = {"scaffold_html": str(scaffold_dir / "scaffold.html"), "scale": scale, "quality": JPEG_QUALITY, "slides": jobs}
    rendered = (renderer or _run_renderer)(job)["slides"]

    checks: list[dict] = []
    outputs = []
    for (label, output, frame, slide), result in zip(plan, rendered):
        if result.get("error"):
            _check(checks, f"{label}:rendered", False, result["error"])
            continue
        outputs.append(output)
        data = output.read_bytes() if output.is_file() else b""
        try:
            size = image_dimensions(data)
        except CropError:
            size = (0, 0)
        _check(checks, f"{label}:rendered",
               size == (composition["width"], composition["height"]) and len(data) <= fmt["max_file_bytes"],
               f"{size[0]}x{size[1]}, {len(data)} bytes")
        for image, target in zip(result["images"], slide["images"]):
            if image["natural_width"] < target["width"] or image["natural_height"] < target["height"]:
                warnings.append(
                    f"{label}: the image in '{image['slot']}' is {image['natural_width']}x{image['natural_height']}, "
                    f"smaller than its {target['width']}x{target['height']} area, and was enlarged"
                )
        if result["logo_loaded"] is not None:
            _check(checks, f"{label}:logo", result["logo_loaded"], "logo image loaded")
        for slot, measured in result["text"].items():
            limit = frame["text_slots"][slot]["max_lines"]
            fits = measured["lines"] <= limit and measured["inside_canvas"]
            message = f"{measured['lines']} of {limit} lines"
            if not measured["inside_canvas"]:
                message += ", runs outside the slide"
            _check(checks, f"{label}:text:{slot}", fits, message)

    passed = bool(checks) and all(check["passed"] for check in checks)
    report = package_dir / RENDER_REPORT
    report.write_text(json.dumps({
        "passed": passed,
        "format": composition["format"], "width": composition["width"], "height": composition["height"],
        "slides": [str(path.relative_to(package_dir)) for path in outputs],
        "warnings": warnings, "checks": checks,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    zip_path = None
    if passed and package["build"]["deliverable"]:
        zip_path = Path(shutil.make_archive(str(package_dir), "zip", root_dir=package_dir.parent, base_dir=package_dir.name))
    return RenderResult(passed, outputs, report, zip_path, checks, warnings)


def _run_renderer(job: dict) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        job_path = Path(tmp) / "job.json"
        job_path.write_text(json.dumps(job), encoding="utf-8")
        try:
            done = subprocess.run(["node", str(RENDERER), "--job", str(job_path)],
                                  capture_output=True, text=True, timeout=600)
        except (OSError, subprocess.TimeoutExpired) as err:
            raise RenderError(f"The slide renderer could not run: {err}") from err
    if done.returncode != 0:
        raise RenderError(f"The slide renderer failed: {done.stderr.strip() or 'no error output'}")
    return json.loads(done.stdout)


def _check(checks: list[dict], name: str, passed: bool, message: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "message": message})
