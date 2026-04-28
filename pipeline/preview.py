"""3D preview renderer — shows the shell with skeleton visible inside.

This is what the customer sees before purchase: their custom character
shell rendered semi-transparently over the standard servo skeleton.

Usage:
    python -m pipeline.preview shell_humanoid.stl skeleton_spark.stl
    python -m pipeline.preview shell_humanoid.stl skeleton_spark.stl --save preview.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import trimesh

from pipeline.skeleton import build_skeleton_for_subtraction, build_skeleton_parts
from pipeline.shell_pipeline import scale_skeleton_to_sculpture


def render_preview(
    shell_path: str | Path,
    sculpture_path: str | Path | None = None,
    skeleton_path: str | Path | None = None,
    save_path: str | Path | None = None,
    title: str = "Your HawaBot",
) -> None:
    """Render a 3D preview of the shell with skeleton inside.

    Shows:
    - Shell mesh in semi-transparent blue
    - Skeleton parts in orange/red (servo housings, wire channels)
    - Joint positions as green dots
    - Multiple viewing angles
    """
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    # Load meshes
    shell = trimesh.load(str(shell_path), force="mesh")

    # Get skeleton parts for colored rendering
    if skeleton_path:
        skeleton_full = trimesh.load(str(skeleton_path), force="mesh")
    else:
        skeleton_full = build_skeleton_for_subtraction()

    # If we have the original sculpture, scale the skeleton to match
    if sculpture_path:
        sculpture = trimesh.load(str(sculpture_path), force="mesh")
        skeleton_full = scale_skeleton_to_sculpture(sculpture, skeleton_full)

    # Create figure with multiple views
    fig = plt.figure(figsize=(16, 8))
    fig.suptitle(f"{title}", fontsize=16, fontweight="bold", y=0.95)
    fig.text(0.5, 0.9, "Semi-transparent shell with internal skeleton",
             ha="center", fontsize=10, color="#666")

    views = [
        ("Front", 10, -80),
        ("Side", 10, -170),
        ("3/4 View", 20, -130),
    ]

    for idx, (view_name, elev, azim) in enumerate(views):
        ax = fig.add_subplot(1, 3, idx + 1, projection="3d")
        ax.set_title(view_name, fontsize=11)

        # Draw shell (semi-transparent)
        _draw_mesh(ax, shell, color="#3B82F6", alpha=0.15, edge_alpha=0.08)

        # Draw skeleton (solid, colored by type)
        _draw_mesh(ax, skeleton_full, color="#EF4444", alpha=0.7, edge_alpha=0.3)

        # Set viewing angle
        ax.view_init(elev=elev, azim=azim)

        # Clean up axes
        _style_3d_axis(ax, shell)

    plt.tight_layout()

    if save_path:
        plt.savefig(str(save_path), dpi=150, bbox_inches="tight",
                    facecolor="white", edgecolor="none")
        print(f"Preview saved to {save_path}")
    else:
        plt.show()


def render_comparison(
    sculpture_path: str | Path,
    shell_path: str | Path,
    skeleton_path: str | Path | None = None,
    save_path: str | Path | None = None,
    title: str = "Your HawaBot — Design to Robot",
) -> None:
    """Render a before/after comparison:
    Left:  Original sculpture (what the kid designed)
    Right: Shell + skeleton (what gets built)
    """
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    sculpture = trimesh.load(str(sculpture_path), force="mesh")
    shell = trimesh.load(str(shell_path), force="mesh")

    if skeleton_path:
        skeleton = trimesh.load(str(skeleton_path), force="mesh")
    else:
        skeleton = build_skeleton_for_subtraction()
    skeleton = scale_skeleton_to_sculpture(sculpture, skeleton)

    fig = plt.figure(figsize=(14, 7))
    fig.suptitle(title, fontsize=16, fontweight="bold", y=0.95)

    elev, azim = 15, -130

    # Left: Original design
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    ax1.set_title("Your Design", fontsize=13)
    _draw_mesh(ax1, sculpture, color="#8B5CF6", alpha=0.5, edge_alpha=0.15)
    ax1.view_init(elev=elev, azim=azim)
    _style_3d_axis(ax1, sculpture)

    # Right: Shell + skeleton
    ax2 = fig.add_subplot(1, 2, 2, projection="3d")
    ax2.set_title("Your Robot (shell + skeleton)", fontsize=13)
    _draw_mesh(ax2, shell, color="#3B82F6", alpha=0.15, edge_alpha=0.08)
    _draw_mesh(ax2, skeleton, color="#EF4444", alpha=0.7, edge_alpha=0.3)
    ax2.view_init(elev=elev, azim=azim)
    _style_3d_axis(ax2, shell)

    plt.tight_layout()

    if save_path:
        plt.savefig(str(save_path), dpi=150, bbox_inches="tight",
                    facecolor="white", edgecolor="none")
        print(f"Comparison saved to {save_path}")
    else:
        plt.show()


def render_exploded(
    shell_path: str | Path,
    skeleton_path: str | Path | None = None,
    sculpture_path: str | Path | None = None,
    save_path: str | Path | None = None,
    title: str = "Inside Your HawaBot",
) -> None:
    """Render an exploded view showing the shell separated from the skeleton.

    The shell is lifted up to reveal the skeleton underneath.
    """
    import matplotlib.pyplot as plt

    shell = trimesh.load(str(shell_path), force="mesh")

    if skeleton_path:
        skeleton = trimesh.load(str(skeleton_path), force="mesh")
    else:
        skeleton = build_skeleton_for_subtraction()

    if sculpture_path:
        sculpture = trimesh.load(str(sculpture_path), force="mesh")
        skeleton = scale_skeleton_to_sculpture(sculpture, skeleton)

    fig = plt.figure(figsize=(8, 10))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title(title, fontsize=14, fontweight="bold")

    # Draw skeleton at original position
    _draw_mesh(ax, skeleton, color="#EF4444", alpha=0.8, edge_alpha=0.3)

    # Draw shell lifted up (exploded view)
    shell_exploded = shell.copy()
    lift = shell.bounding_box.extents[2] * 0.6  # Lift by 60% of height
    shell_exploded.apply_translation([0, 0, lift])
    _draw_mesh(ax, shell_exploded, color="#3B82F6", alpha=0.25, edge_alpha=0.1)

    # Draw guide lines connecting shell to skeleton
    center = shell.bounding_box.centroid
    ax.plot([center[0], center[0]], [center[1], center[1]],
            [center[2], center[2] + lift],
            '--', color="#94A3B8", alpha=0.5, linewidth=1)

    ax.view_init(elev=20, azim=-130)

    # Combine bounds for axis scaling
    all_verts = np.vstack([skeleton.vertices, shell_exploded.vertices])
    _style_3d_axis_from_bounds(ax, all_verts)

    plt.tight_layout()

    if save_path:
        plt.savefig(str(save_path), dpi=150, bbox_inches="tight",
                    facecolor="white", edgecolor="none")
        print(f"Exploded view saved to {save_path}")
    else:
        plt.show()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _draw_mesh(
    ax,
    mesh: trimesh.Trimesh,
    color: str = "#3B82F6",
    alpha: float = 0.3,
    edge_alpha: float = 0.1,
) -> None:
    """Draw a trimesh on a matplotlib 3D axis."""
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    from matplotlib.colors import to_rgba

    # Subsample faces if there are too many (matplotlib gets slow >5000)
    faces = mesh.faces
    verts = mesh.vertices

    if len(faces) > 5000:
        # Subsample faces for rendering performance
        indices = np.random.choice(len(faces), 5000, replace=False)
        faces = faces[indices]

    triangles = verts[faces]

    face_color = to_rgba(color, alpha)
    edge_color = to_rgba(color, edge_alpha)

    collection = Poly3DCollection(
        triangles,
        facecolors=[face_color] * len(triangles),
        edgecolors=[edge_color] * len(triangles),
        linewidths=0.3,
    )
    ax.add_collection3d(collection)


def _style_3d_axis(ax, mesh: trimesh.Trimesh) -> None:
    """Style a 3D axis with proper limits and clean appearance."""
    _style_3d_axis_from_bounds(ax, mesh.vertices)


def _style_3d_axis_from_bounds(ax, vertices: np.ndarray) -> None:
    """Style a 3D axis from vertex bounds."""
    mins = vertices.min(axis=0)
    maxs = vertices.max(axis=0)
    center = (mins + maxs) / 2
    max_range = (maxs - mins).max() / 2 * 1.2

    ax.set_xlim(center[0] - max_range, center[0] + max_range)
    ax.set_ylim(center[1] - max_range, center[1] + max_range)
    ax.set_zlim(center[2] - max_range, center[2] + max_range)

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_zlabel("")
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor("white")
    ax.yaxis.pane.set_edgecolor("white")
    ax.zaxis.pane.set_edgecolor("white")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m pipeline.preview <shell.stl> [skeleton.stl] [--save output.png]")
        print("  python -m pipeline.preview --compare <sculpture.stl> <shell.stl> [--save output.png]")
        print("  python -m pipeline.preview --exploded <shell.stl> [skeleton.stl] [--save output.png]")
        print("\nRunning demo with test files...")

        # Generate test data if needed
        from pipeline.shell_pipeline import run_pipeline
        import os

        if not os.path.exists("shell_humanoid.stl"):
            print("Run `python -m pipeline.shell_pipeline` first to generate test shells.")
            sys.exit(1)

        # Comparison view
        print("\nRendering comparison view...")
        render_comparison(
            "test_humanoid.stl", "shell_humanoid.stl",
            save_path="preview_comparison.png",
            title="Your HawaBot — Design to Robot",
        )

        # Shell + skeleton preview
        print("Rendering preview...")
        render_preview(
            "shell_humanoid.stl",
            sculpture_path="test_humanoid.stl",
            save_path="preview_shell.png",
            title="Bolt — Humanoid Companion",
        )

        # Exploded view
        print("Rendering exploded view...")
        render_exploded(
            "shell_humanoid.stl",
            sculpture_path="test_humanoid.stl",
            save_path="preview_exploded.png",
            title="Inside Your HawaBot",
        )

        print("\nDone! Check preview_comparison.png, preview_shell.png, preview_exploded.png")

    elif sys.argv[1] == "--compare":
        sculpture = sys.argv[2]
        shell = sys.argv[3]
        save = sys.argv[sys.argv.index("--save") + 1] if "--save" in sys.argv else None
        render_comparison(sculpture, shell, save_path=save)

    elif sys.argv[1] == "--exploded":
        shell = sys.argv[2]
        skeleton = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else None
        save = sys.argv[sys.argv.index("--save") + 1] if "--save" in sys.argv else None
        render_exploded(shell, skeleton_path=skeleton, save_path=save)

    else:
        shell = sys.argv[1]
        skeleton = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
        save = sys.argv[sys.argv.index("--save") + 1] if "--save" in sys.argv else None
        render_preview(shell, skeleton_path=skeleton, save_path=save)
