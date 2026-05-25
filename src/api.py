#!/usr/bin/env python3
"""
Entry point: python -m src.api
Starts the TrustedChain HTTP server (server.py).
"""
import os
import sys
from pathlib import Path

# Ensure repo root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server import run

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "4173"))
    run(host=host, port=port)
