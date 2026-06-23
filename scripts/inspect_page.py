"""Legacy wrapper for page inspection."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pax_simulator.utils.inspect import inspect_register_page

if __name__ == "__main__":
    inspect_register_page()
