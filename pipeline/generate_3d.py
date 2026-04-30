"""3D model generation from images or text descriptions.

Wraps Tripo3D (primary) and Meshy (fallback) APIs to generate
watertight 3D meshes from customer input.

Usage:
    from pipeline.generate_3d import generate_from_image, generate_from_text

    # Image to 3D
    mesh_path = generate_from_image("photo.jpg", output_dir="output/")

    # Text to 3D
    mesh_path = generate_from_text(
        "A samurai cat with a red cape",
        output_dir="output/",
    )

Environment variables:
    TRIPO_API_KEY    — Tripo3D API key (https://www.tripo3d.ai/api)
    MESHY_API_KEY    — Meshy API key (https://docs.meshy.ai)

Set HAWABOT_3D_PROVIDER to "meshy" to use Meshy as primary instead.
"""

from __future__ import annotations

import os
import time
import json
import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen, urlretrieve
from urllib.error import HTTPError
from urllib.parse import urlencode


# ── Configuration ─────────────────────────────────────────────────────────

TRIPO_API_BASE = "https://api.tripo3d.ai/v2/openapi"
MESHY_API_BASE = "https://api.meshy.ai/openapi/v2"

TRIPO_API_KEY = os.environ.get("TRIPO_API_KEY", "")
MESHY_API_KEY = os.environ.get("MESHY_API_KEY", "")

DEFAULT_PROVIDER = os.environ.get("HAWABOT_3D_PROVIDER", "tripo")


# ── T-Pose Enforcement ────────────────────────────────────────────────────

# This suffix is appended to ALL generation prompts to ensure the output
# model has arms spread out and legs apart for clean zone dissection.
TPOSE_PROMPT_SUFFIX = (
    ". The character must be standing in a T-pose: arms held straight out "
    "to the sides at shoulder height, palms facing down, legs shoulder-width "
    "apart, feet flat on the ground, facing directly forward. "
    "Full body visible, no accessories blocking the arms or legs."
)

# For image-to-3D, this is used as the text guidance alongside the image
# to steer the model toward T-pose output.
TPOSE_IMAGE_GUIDANCE = (
    "Generate this character in a T-pose with arms straight out to the sides "
    "at shoulder height, legs shoulder-width apart, standing upright facing "
    "forward. Full body, centered."
)


def _enforce_tpose_prompt(prompt: str) -> str:
    """Append T-pose instructions to a generation prompt.

    Avoids double-appending if the prompt already mentions T-pose.
    """
    if "t-pose" in prompt.lower() or "t pose" in prompt.lower():
        return prompt
    return prompt.rstrip(". ") + TPOSE_PROMPT_SUFFIX


@dataclass
class GenerationResult:
    """Result of a 3D model generation."""
    success: bool
    mesh_path: str | None          # Path to downloaded mesh file
    provider: str                  # "tripo" or "meshy"
    task_id: str | None            # Provider's task ID for tracking
    duration_seconds: float        # Time from request to download
    cost_estimate: str             # Estimated cost string
    error: str | None


# ── HTTP Helpers ──────────────────────────────────────────────────────────

def _api_request(
    url: str,
    method: str = "GET",
    data: dict | None = None,
    headers: dict | None = None,
    files: dict | None = None,
) -> dict:
    """Make an API request and return parsed JSON response."""
    if headers is None:
        headers = {}

    if files:
        # Multipart form data for file uploads
        import io
        boundary = "----HawaBotBoundary"
        body_parts = []

        for key, (filename, filedata, content_type) in files.items():
            body_parts.append(f"--{boundary}\r\n".encode())
            body_parts.append(
                f'Content-Disposition: form-data; name="{key}"; '
                f'filename="{filename}"\r\n'.encode()
            )
            body_parts.append(f"Content-Type: {content_type}\r\n\r\n".encode())
            body_parts.append(filedata)
            body_parts.append(b"\r\n")

        if data:
            for key, value in data.items():
                body_parts.append(f"--{boundary}\r\n".encode())
                body_parts.append(
                    f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode()
                )
                body_parts.append(str(value).encode())
                body_parts.append(b"\r\n")

        body_parts.append(f"--{boundary}--\r\n".encode())
        body = b"".join(body_parts)
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    elif data:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    else:
        body = None

    req = Request(url, data=body, headers=headers, method=method)
    resp = urlopen(req, timeout=120)
    return json.loads(resp.read().decode())


def _poll_task(
    url: str,
    headers: dict,
    timeout: int = 300,
    interval: int = 5,
) -> dict:
    """Poll a task endpoint until completion or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        result = _api_request(url, headers=headers)
        status = result.get("data", {}).get("status", result.get("status", ""))

        if status in ("SUCCEEDED", "succeeded", "completed"):
            return result
        elif status in ("FAILED", "failed", "error"):
            raise RuntimeError(f"Task failed: {result}")

        time.sleep(interval)

    raise TimeoutError(f"Task timed out after {timeout}s")


# ── Tripo3D Provider ──────────────────────────────────────────────────────

def _tripo_headers() -> dict:
    if not TRIPO_API_KEY:
        raise ValueError("TRIPO_API_KEY environment variable not set")
    return {"Authorization": f"Bearer {TRIPO_API_KEY}"}


def _tripo_from_image(image_path: str, output_dir: str) -> GenerationResult:
    """Generate 3D model from image using Tripo3D API."""
    start = time.time()
    headers = _tripo_headers()

    # Step 1: Upload image
    img_path = Path(image_path)
    with open(img_path, "rb") as f:
        image_data = f.read()

    content_type = "image/jpeg"
    if img_path.suffix.lower() == ".png":
        content_type = "image/png"

    upload_resp = _api_request(
        f"{TRIPO_API_BASE}/upload",
        method="POST",
        headers=headers,
        files={"file": (img_path.name, image_data, content_type)},
    )
    image_token = upload_resp.get("data", {}).get("image_token", "")

    # Step 2: Create generation task with T-pose guidance
    task_resp = _api_request(
        f"{TRIPO_API_BASE}/task",
        method="POST",
        headers=headers,
        data={
            "type": "image_to_model",
            "file": {"type": "image", "file_token": image_token},
            "prompt": TPOSE_IMAGE_GUIDANCE,
            "model_version": "v2.5-20250123",
        },
    )
    task_id = task_resp.get("data", {}).get("task_id", "")

    # Step 3: Poll for completion
    result = _poll_task(
        f"{TRIPO_API_BASE}/task/{task_id}",
        headers=headers,
    )

    # Step 4: Download model
    model_url = (
        result.get("data", {}).get("output", {}).get("model", "")
    )
    if not model_url:
        # Try alternative response format
        model_url = result.get("data", {}).get("result", {}).get("model", {}).get("url", "")

    if not model_url:
        return GenerationResult(
            success=False, mesh_path=None, provider="tripo",
            task_id=task_id, duration_seconds=time.time() - start,
            cost_estimate="~$0.20", error="No model URL in response",
        )

    out_path = Path(output_dir) / f"generated_{task_id}.glb"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(model_url, str(out_path))

    return GenerationResult(
        success=True, mesh_path=str(out_path), provider="tripo",
        task_id=task_id, duration_seconds=time.time() - start,
        cost_estimate="~$0.20 (via API)", error=None,
    )


def _tripo_from_text(prompt: str, output_dir: str) -> GenerationResult:
    """Generate 3D model from text using Tripo3D API."""
    start = time.time()
    headers = _tripo_headers()

    # Enforce T-pose in prompt
    prompt = _enforce_tpose_prompt(prompt)

    # Create text-to-model task
    task_resp = _api_request(
        f"{TRIPO_API_BASE}/task",
        method="POST",
        headers=headers,
        data={
            "type": "text_to_model",
            "prompt": prompt,
            "model_version": "v2.5-20250123",
        },
    )
    task_id = task_resp.get("data", {}).get("task_id", "")

    # Poll for completion
    result = _poll_task(
        f"{TRIPO_API_BASE}/task/{task_id}",
        headers=headers,
    )

    # Download model
    model_url = (
        result.get("data", {}).get("output", {}).get("model", "")
    )
    if not model_url:
        model_url = result.get("data", {}).get("result", {}).get("model", {}).get("url", "")

    if not model_url:
        return GenerationResult(
            success=False, mesh_path=None, provider="tripo",
            task_id=task_id, duration_seconds=time.time() - start,
            cost_estimate="~$0.20", error="No model URL in response",
        )

    out_path = Path(output_dir) / f"generated_{task_id}.glb"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(model_url, str(out_path))

    return GenerationResult(
        success=True, mesh_path=str(out_path), provider="tripo",
        task_id=task_id, duration_seconds=time.time() - start,
        cost_estimate="~$0.20 (via API)", error=None,
    )


# ── Meshy Provider ────────────────────────────────────────────────────────

def _meshy_headers() -> dict:
    if not MESHY_API_KEY:
        raise ValueError("MESHY_API_KEY environment variable not set")
    return {"Authorization": f"Bearer {MESHY_API_KEY}"}


def _meshy_from_image(image_path: str, output_dir: str) -> GenerationResult:
    """Generate 3D model from image using Meshy API."""
    start = time.time()
    headers = _meshy_headers()

    # Meshy image-to-3D uses base64-encoded image or URL
    img_path = Path(image_path)
    with open(img_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    content_type = "image/jpeg"
    if img_path.suffix.lower() == ".png":
        content_type = "image/png"

    data_uri = f"data:{content_type};base64,{image_b64}"

    # Create image-to-3D task with T-pose guidance
    task_resp = _api_request(
        f"{MESHY_API_BASE}/image-to-3d",
        method="POST",
        headers=headers,
        data={
            "image_url": data_uri,
            "prompt": TPOSE_IMAGE_GUIDANCE,
            "enable_pbr": True,
            "should_remesh": True,
            "topology": "quad",
        },
    )
    task_id = task_resp.get("result", "")

    # Poll for completion
    result = _poll_task(
        f"{MESHY_API_BASE}/image-to-3d/{task_id}",
        headers=headers,
        interval=10,  # Meshy is slower
    )

    # Download model (GLB format)
    model_url = result.get("model_urls", {}).get("glb", "")
    if not model_url:
        model_url = result.get("data", {}).get("model_urls", {}).get("glb", "")

    if not model_url:
        return GenerationResult(
            success=False, mesh_path=None, provider="meshy",
            task_id=task_id, duration_seconds=time.time() - start,
            cost_estimate="~$0.05 (20 credits)", error="No model URL in response",
        )

    out_path = Path(output_dir) / f"generated_{task_id}.glb"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(model_url, str(out_path))

    return GenerationResult(
        success=True, mesh_path=str(out_path), provider="meshy",
        task_id=task_id, duration_seconds=time.time() - start,
        cost_estimate="~$0.05 (20 credits)", error=None,
    )


def _meshy_from_text(prompt: str, output_dir: str) -> GenerationResult:
    """Generate 3D model from text using Meshy API."""
    start = time.time()
    headers = _meshy_headers()

    # Enforce T-pose in prompt
    prompt = _enforce_tpose_prompt(prompt)

    # Create text-to-3D task
    task_resp = _api_request(
        f"{MESHY_API_BASE}/text-to-3d",
        method="POST",
        headers=headers,
        data={
            "prompt": prompt,
            "art_style": "realistic",
            "should_remesh": True,
            "topology": "quad",
        },
    )
    task_id = task_resp.get("result", "")

    # Poll for completion
    result = _poll_task(
        f"{MESHY_API_BASE}/text-to-3d/{task_id}",
        headers=headers,
        interval=10,
    )

    # Download model
    model_url = result.get("model_urls", {}).get("glb", "")
    if not model_url:
        model_url = result.get("data", {}).get("model_urls", {}).get("glb", "")

    if not model_url:
        return GenerationResult(
            success=False, mesh_path=None, provider="meshy",
            task_id=task_id, duration_seconds=time.time() - start,
            cost_estimate="~$0.03 (10 credits)", error="No model URL in response",
        )

    out_path = Path(output_dir) / f"generated_{task_id}.glb"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(model_url, str(out_path))

    return GenerationResult(
        success=True, mesh_path=str(out_path), provider="meshy",
        task_id=task_id, duration_seconds=time.time() - start,
        cost_estimate="~$0.03 (10 credits)", error=None,
    )


# ── T-Pose Validation ─────────────────────────────────────────────────────

def _validate_tpose_on_mesh(mesh_path: str) -> tuple[bool, list[str]]:
    """Load a generated mesh and check if it's in T-pose.

    Returns (is_tpose, warnings).
    """
    import trimesh
    from pipeline.dissect import validate_tpose
    from pipeline.skeleton import DEFAULT_CUT_PLANES
    from pipeline.shell_pipeline import load_and_prepare

    try:
        mesh = load_and_prepare(mesh_path)
        return validate_tpose(mesh, DEFAULT_CUT_PLANES)
    except Exception as e:
        return False, [f"Could not validate T-pose: {e}"]


def _describe_image_for_text_fallback(image_path: str) -> str:
    """Generate a text description from an image for text-only fallback.

    In production, this would use a vision model (Claude, GPT-4V) to
    describe the character. For now, returns a generic prompt derived
    from the filename.
    """
    name = Path(image_path).stem
    # Clean up filename into a readable description
    description = name.replace("-", " ").replace("_", " ").replace(".", " ")
    description = " ".join(w.capitalize() for w in description.split())
    return f"A detailed action figure character of {description}, full body"


# ── Public API ────────────────────────────────────────────────────────────

def generate_from_image(
    image_path: str,
    output_dir: str = "pipeline/output",
    provider: str | None = None,
    character_description: str | None = None,
) -> GenerationResult:
    """Generate a 3D model from an image, with T-pose validation + fallback.

    Strategy:
    1. Try image-to-3D with T-pose text guidance
    2. Validate the result is actually in T-pose
    3. If not T-pose → retry as text-only using character description
       (ignores image geometry, uses it only for style reference)

    Args:
        image_path: Path to input image (JPG, PNG).
        output_dir: Directory for output mesh file.
        provider: "tripo" or "meshy". Defaults to HAWABOT_3D_PROVIDER env var.
        character_description: Text description of the character. Used for
            text-only fallback if image-to-3D doesn't produce T-pose.
            If None, a description is derived from the filename.

    Returns:
        GenerationResult with path to downloaded mesh.
    """
    provider = provider or DEFAULT_PROVIDER

    # ── Pass 1: Image-to-3D with T-pose guidance ──────────────────────
    print(f"Pass 1: Image-to-3D with T-pose guidance ({provider})...")
    try:
        if provider == "tripo":
            result = _tripo_from_image(image_path, output_dir)
        elif provider == "meshy":
            result = _meshy_from_image(image_path, output_dir)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    except Exception as e:
        # Try fallback provider for image pass
        fallback = "meshy" if provider == "tripo" else "tripo"
        try:
            print(f"  {provider} failed: {e}. Trying {fallback}...")
            if fallback == "tripo":
                result = _tripo_from_image(image_path, output_dir)
            else:
                result = _meshy_from_image(image_path, output_dir)
        except Exception as e2:
            result = GenerationResult(
                success=False, mesh_path=None, provider=provider,
                task_id=None, duration_seconds=0,
                cost_estimate="N/A",
                error=f"Image-to-3D failed on both providers: {e}, {e2}",
            )

    if not result.success or not result.mesh_path:
        return result

    # ── T-Pose Validation ─────────────────────────────────────────────
    print("  Validating T-pose...")
    is_tpose, tpose_warnings = _validate_tpose_on_mesh(result.mesh_path)

    if is_tpose:
        print("  ✓ T-pose confirmed.")
        return result

    print(f"  ✗ Not in T-pose: {'; '.join(tpose_warnings)}")

    # ── Pass 2: Text-only fallback ────────────────────────────────────
    # The image overpowered the T-pose guidance, so we fall back to
    # text-only generation where we have full control over the pose.
    if character_description is None:
        character_description = _describe_image_for_text_fallback(image_path)

    print(f"Pass 2: Text-only fallback with T-pose prompt...")
    print(f"  Description: \"{character_description}\"")

    text_result = generate_from_text(
        prompt=character_description,
        output_dir=output_dir,
        provider=provider,
    )

    if not text_result.success:
        # Text fallback also failed — return the original image result
        # with T-pose warnings attached
        print("  ✗ Text fallback also failed. Using image result with warnings.")
        result.error = (
            f"T-pose validation failed ({'; '.join(tpose_warnings)}). "
            f"Text fallback failed: {text_result.error}"
        )
        return result

    # Validate the text result too
    is_tpose_2, warnings_2 = _validate_tpose_on_mesh(text_result.mesh_path)
    if is_tpose_2:
        print("  ✓ T-pose confirmed on text fallback.")
    else:
        print(f"  ⚠ Text fallback also not in T-pose: {'; '.join(warnings_2)}")
        text_result.error = (
            f"Warning: T-pose not confirmed even after text fallback. "
            f"{'; '.join(warnings_2)}"
        )

    # Accumulate cost from both passes
    total_duration = result.duration_seconds + text_result.duration_seconds
    text_result.duration_seconds = total_duration
    text_result.cost_estimate = f"~2× ({result.cost_estimate} + {text_result.cost_estimate})"

    return text_result


def generate_from_text(
    prompt: str,
    output_dir: str = "pipeline/output",
    provider: str | None = None,
) -> GenerationResult:
    """Generate a 3D model from a text description.

    T-pose is enforced automatically via prompt injection.

    Args:
        prompt: Text description of the character.
        output_dir: Directory for output mesh file.
        provider: "tripo" or "meshy". Defaults to HAWABOT_3D_PROVIDER env var.

    Returns:
        GenerationResult with path to downloaded mesh.
    """
    provider = provider or DEFAULT_PROVIDER

    try:
        if provider == "tripo":
            return _tripo_from_text(prompt, output_dir)
        elif provider == "meshy":
            return _meshy_from_text(prompt, output_dir)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    except Exception as e:
        fallback = "meshy" if provider == "tripo" else "tripo"
        try:
            print(f"Primary provider ({provider}) failed: {e}")
            print(f"Trying fallback ({fallback})...")
            if fallback == "tripo":
                return _tripo_from_text(prompt, output_dir)
            else:
                return _meshy_from_text(prompt, output_dir)
        except Exception as e2:
            return GenerationResult(
                success=False, mesh_path=None, provider=provider,
                task_id=None, duration_seconds=0,
                cost_estimate="N/A",
                error=f"Both providers failed. Primary: {e}. Fallback: {e2}",
            )


def mesh_to_trimesh(glb_path: str):
    """Convert a downloaded GLB file to a trimesh for pipeline use."""
    import trimesh
    mesh = trimesh.load(glb_path, force="mesh")
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fill_holes(mesh)
    return mesh
