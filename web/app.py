"""HawaBot Design Platform — Web prototype.

A Flask app that demonstrates the full customer journey:
1. Describe or upload a character design
2. Generate a 3D model (via Meshy API or mock)
3. Run the shell pipeline (subtract skeleton, split sections)
4. Preview in an interactive 3D viewer
5. Select tier and plan

Run: python web/app.py
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

app = Flask(__name__, template_folder="templates", static_folder="static")

# Where we store generated models and pipeline outputs
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Project root for accessing pipeline modules
PROJECT_ROOT = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate_model():
    """Generate a 3D model from text prompt or uploaded image.

    For now, uses a pre-generated STL as a mock. When Meshy API key is
    configured, this will call the real API.
    """
    design_id = str(uuid.uuid4())[:8]
    design_dir = UPLOAD_DIR / design_id
    design_dir.mkdir(exist_ok=True)

    # Check if an image was uploaded
    if "image" in request.files:
        image = request.files["image"]
        image_path = design_dir / "input.png"
        image.save(str(image_path))

    prompt = request.form.get("prompt", "robot character")

    # Check for Meshy API key
    meshy_key = os.environ.get("MESHY_API_KEY")

    if meshy_key:
        # Real Meshy API integration
        sculpture_path = _generate_via_meshy(meshy_key, design_dir, prompt)
    else:
        # Mock: use the Naruto STL if available, otherwise generate a test shape
        naruto_path = Path.home() / "Downloads" / "teen-naruto-figurine-anime-collectible-3d-printable-model_files" / "teen-naruto.stl"
        if naruto_path.exists():
            sculpture_path = design_dir / "sculpture.stl"
            shutil.copy(naruto_path, sculpture_path)
        else:
            sculpture_path = _generate_test_sculpture(design_dir)

    # Run the shell pipeline
    result = _run_pipeline(design_dir, sculpture_path)

    return jsonify({
        "design_id": design_id,
        "status": "success" if result["success"] else "error",
        "sculpture_url": f"/api/model/{design_id}/sculpture.glb",
        "shell_url": f"/api/model/{design_id}/shell.glb",
        "skeleton_url": f"/api/model/{design_id}/skeleton.glb",
        "sections": result.get("sections", {}),
        "metrics": result.get("metrics", {}),
    })


@app.route("/api/model/<design_id>/<filename>")
def serve_model(design_id, filename):
    """Serve a generated 3D model file."""
    filepath = UPLOAD_DIR / design_id / filename
    if not filepath.exists():
        # Try STL version and convert
        stl_name = filename.replace(".glb", ".stl")
        stl_path = UPLOAD_DIR / design_id / stl_name
        if stl_path.exists():
            return send_file(str(stl_path), mimetype="application/octet-stream")
        return jsonify({"error": "File not found"}), 404
    return send_file(str(filepath), mimetype="application/octet-stream")


def _generate_via_meshy(api_key: str, design_dir: Path, prompt: str) -> Path:
    """Call Meshy API to generate a 3D model. Returns path to sculpture STL."""
    import time
    import urllib.request

    # Check if there's an uploaded image
    image_path = design_dir / "input.png"

    if image_path.exists():
        # Image to 3D
        import base64
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()

        payload = json.dumps({
            "image_url": f"data:image/png;base64,{image_b64}",
            "ai_model": "meshy-6",
            "target_formats": ["stl"],
        })
        endpoint = "https://api.meshy.ai/openapi/v1/image-to-3d"
    else:
        # Text to 3D (preview stage)
        payload = json.dumps({
            "prompt": prompt,
            "ai_model": "meshy-6",
            "target_formats": ["stl"],
        })
        endpoint = "https://api.meshy.ai/openapi/v2/text-to-3d"

    # Submit task
    req = urllib.request.Request(
        endpoint,
        data=payload.encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        task = json.loads(resp.read())
    task_id = task.get("result")

    # Poll for completion
    poll_url = f"{endpoint}/{task_id}"
    for _ in range(120):  # Max 2 minutes
        time.sleep(2)
        req = urllib.request.Request(
            poll_url,
            headers={"Authorization": f"Bearer {api_key}"},
        )
        with urllib.request.urlopen(req) as resp:
            status = json.loads(resp.read())

        if status.get("status") == "SUCCEEDED":
            # Download the STL
            model_urls = status.get("model_urls", {})
            stl_url = model_urls.get("stl") or model_urls.get("glb") or model_urls.get("obj")
            if stl_url:
                sculpture_path = design_dir / "sculpture.stl"
                urllib.request.urlretrieve(stl_url, str(sculpture_path))
                return sculpture_path

        elif status.get("status") == "FAILED":
            raise Exception(f"Meshy generation failed: {status.get('message', 'Unknown error')}")

    raise Exception("Meshy generation timed out")


def _generate_test_sculpture(design_dir: Path) -> Path:
    """Generate a simple test sculpture for demo purposes."""
    import numpy as np
    import trimesh
    import manifold3d as mf

    def to_mf(mesh):
        return mf.Manifold(mf.Mesh(
            vert_properties=np.array(mesh.vertices, dtype=np.float32),
            tri_verts=np.array(mesh.faces, dtype=np.uint32),
        ))

    def to_trimesh(manifold):
        out = manifold.to_mesh()
        return trimesh.Trimesh(vertices=out.vert_properties[:, :3], faces=out.tri_verts)

    torso = trimesh.creation.capsule(height=70, radius=35)
    torso.apply_translation([0, 0, 30])
    head = trimesh.creation.icosphere(radius=28, subdivisions=3)
    head.apply_translation([0, 0, 95])
    l_arm = trimesh.creation.capsule(height=55, radius=12)
    l_arm.apply_translation([-42, 0, 50])
    r_arm = trimesh.creation.capsule(height=55, radius=12)
    r_arm.apply_translation([42, 0, 50])

    combined = to_mf(torso) + to_mf(head) + to_mf(l_arm) + to_mf(r_arm)
    mesh = to_trimesh(combined)

    path = design_dir / "sculpture.stl"
    mesh.export(str(path))
    return path


def _run_pipeline(design_dir: Path, sculpture_path: Path) -> dict:
    """Run the full shell pipeline on a sculpture."""
    from pipeline.skeleton import build_skeleton_for_subtraction
    from pipeline.shell_pipeline import run_pipeline
    from pipeline.joint_cuts import cut_joint_clearances, split_shell

    # Build skeleton
    skeleton_path = design_dir / "skeleton.stl"
    skeleton = build_skeleton_for_subtraction()
    skeleton.export(str(skeleton_path))

    # Run main pipeline
    shell_path = design_dir / "shell.stl"
    result = run_pipeline(
        str(sculpture_path), str(skeleton_path), str(shell_path),
        wall_thickness_mm=3.0,
    )

    if not result.success:
        return {"success": False, "errors": result.errors}

    import trimesh

    # Joint clearance cuts
    shell = trimesh.load(str(shell_path), force="mesh")
    skeleton_mesh = trimesh.load(str(skeleton_path), force="mesh")
    skel_height = skeleton_mesh.bounding_box.extents[2]
    shell_height = shell.bounding_box.extents[2]
    scale_factor = shell_height / (skel_height * 1.3)

    shell = cut_joint_clearances(shell, scale_factor)
    shell.export(str(shell_path))

    # Split into sections
    sections = split_shell(shell, scale_factor)
    section_info = {}
    for name, section_mesh in sections.items():
        section_path = design_dir / f"section_{name}.stl"
        section_mesh.export(str(section_path))
        size = section_mesh.bounding_box.extents
        section_info[name] = {
            "vertices": len(section_mesh.vertices),
            "watertight": section_mesh.is_watertight,
            "size_mm": [round(s, 1) for s in size],
            "volume_cm3": round(abs(section_mesh.volume) / 1000, 1) if section_mesh.is_watertight else None,
        }

    # Compute metrics
    sculpture = trimesh.load(str(sculpture_path), force="mesh")
    total_vol = sum(s.get("volume_cm3", 0) or 0 for s in section_info.values())

    return {
        "success": True,
        "sections": section_info,
        "metrics": {
            "total_volume_cm3": round(total_vol, 1),
            "est_weight_g": round(total_vol * 1.24 * 0.2, 0),
            "est_pla_cost": round(total_vol * 1.24 * 0.2 * 0.025, 2),
            "all_watertight": all(s["watertight"] for s in section_info.values()),
        },
    }


if __name__ == "__main__":
    print("\n  HawaBot Design Platform")
    print("  http://localhost:5001\n")
    if os.environ.get("MESHY_API_KEY"):
        print("  Meshy API: CONNECTED")
    else:
        print("  Meshy API: MOCK MODE (set MESHY_API_KEY to enable)")
    print()
    app.run(debug=True, port=5001)
