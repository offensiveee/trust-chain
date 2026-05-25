#!/usr/bin/env python3
"""
Entry point: python -m src.train
Trains the TrustedChain LightGBM model.

Usage:
    python -m src.train
    python src/train.py

Data must be at: training_data/crtsh_5m_labeled.csv
Output model:    models/lightgbm_fast.joblib
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from train_model import main

if __name__ == "__main__":
    sys.exit(main() or 0)
