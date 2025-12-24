#!/usr/bin/env python3
# run_client.py
"""
Script chạy client
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.game_client import main

if __name__ == "__main__":
    main()