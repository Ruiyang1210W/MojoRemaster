import os
import sys
from pathlib import Path

# Windows defaults stdout/stderr to the system codepage (gbk) whenever they
# aren't attached to a real console (redirected to a file, piped, etc.),
# which can't encode the emoji used throughout these scripts' print()
# statements. Force UTF-8 so output never crashes regardless of how it's run.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EPS_DIR = PROJECT_ROOT / "Eps"
MODELS_DIR = PROJECT_ROOT / "models"


def episode_dir(ep: int) -> Path:
    """Return Eps/epNN, creating it if it doesn't exist yet."""
    ep_dir = EPS_DIR / f"ep{ep:02d}"
    ep_dir.mkdir(parents=True, exist_ok=True)
    return ep_dir


def find_source(ep_dir: Path) -> Path:
    """Locate the episode's source video/audio file, named source.<ext>."""
    matches = sorted(ep_dir.glob("source.*"))
    if not matches:
        raise FileNotFoundError(
            f"No source file found in {ep_dir}. "
            f"Drop the episode video/audio in there named 'source.<ext>' "
            f"(e.g. source.mp4)."
        )
    if len(matches) > 1:
        raise FileNotFoundError(
            f"Multiple source.* files found in {ep_dir}: {matches}. "
            f"Keep exactly one."
        )
    return matches[0]


def setup_cuda_dlls() -> None:
    """Register the pip-installed CUDA 12 cuBLAS/cuDNN DLL folders on Windows.

    ctranslate2 (faster-whisper's backend) needs cublas64_12.dll, but a
    system-wide CUDA Toolkit install may ship a different major version
    (e.g. v13), which has a different DLL name and won't satisfy it. The
    nvidia-cublas-cu12 / nvidia-cudnn-cu12 pip packages provide the correct
    DLLs in the venv, but Windows won't find them unless we register the
    folders explicitly.
    """
    if sys.platform != "win32":
        return
    venv_site_packages = PROJECT_ROOT / ".venv" / "Lib" / "site-packages"
    for pkg_bin in (r"nvidia\cublas\bin", r"nvidia\cudnn\bin"):
        dll_dir = venv_site_packages / pkg_bin
        if dll_dir.is_dir():
            os.add_dll_directory(str(dll_dir))
