"""
Pytest configuration — adds backend/ to sys.path so imports work.
"""
import sys
import os

# Make sure backend/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
