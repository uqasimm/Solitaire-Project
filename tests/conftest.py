import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BACKEND_PATH = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_PATH))