"""Shared test configuration.

Importing ``Main`` runs a module-level integrity gate and reads a handful of
optional JSON "db" files from the working directory (falling back to defaults
when they are absent). Neither performs any network I/O, so importing the
module inside the test process is safe.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import Main  # noqa: E402  (import after sys.path tweak)


def get_main():
    return Main
