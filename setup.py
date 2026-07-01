# -*- coding: utf-8 -*-
"""
setup.py - One-time setup script for OncoSight
Run this ONCE before launching the app:
    python setup.py
"""
import os
import sys
import shutil

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
PARENT    = os.path.dirname(BASE_DIR)   # original project root

# Directories to create
DIRS = [
    os.path.join(BASE_DIR, "models"),
    os.path.join(BASE_DIR, "reports"),
    os.path.join(BASE_DIR, "uploads"),
    os.path.join(BASE_DIR, "assets"),
    os.path.join(BASE_DIR, ".streamlit"),
]

print("=" * 60)
print("  OncoSight - Project Setup")
print("=" * 60)

for d in DIRS:
    os.makedirs(d, exist_ok=True)
    print("  [OK] Directory: {}/".format(os.path.relpath(d, BASE_DIR)))

# Copy ML assets
COPY_MAP = {
    os.path.join("models",       "final_best_model.pkl"): os.path.join("models", "final_best_model.pkl"),
    os.path.join("preprocessed", "scaler.pkl"):           os.path.join("models", "scaler.pkl"),
    os.path.join("preprocessed", "feature_names.pkl"):    os.path.join("models", "feature_names.pkl"),
}

print()
print("  Copying ML assets ...")
all_ok = True
for src_rel, dst_rel in COPY_MAP.items():
    src = os.path.join(PARENT, src_rel)
    dst = os.path.join(BASE_DIR, dst_rel)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print("  [OK] Copied: {} -> models/".format(os.path.basename(src)))
    else:
        print("  [!!] NOT FOUND: {}".format(src))
        print("       Please copy it manually to: {}".format(dst))
        all_ok = False

# Initialize database
print()
print("  Initialising database ...")
sys.path.insert(0, BASE_DIR)
try:
    from utils.database import init_db
    init_db()
    print("  [OK] database.db created with default admin account")
except Exception as e:
    print("  [!!] DB init failed: {}".format(e))
    all_ok = False

# Done
print()
if all_ok:
    print("  [SUCCESS] Setup complete!")
    print()
    print("  Launch the app with:")
    print("      streamlit run app.py")
    print()
    print("  Default admin login:")
    print("      Email:    admin@oncosight.ai")
    print("      Password: Admin@123")
else:
    print("  [WARNING] Setup completed with warnings. Review messages above.")
print("=" * 60)
