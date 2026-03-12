#!/usr/bin/env python3
"""
Quick viewer for AWS Architecture Diagrams

This script opens all generated diagrams for easy viewing.
"""

import os
import subprocess
import sys

def open_file(filepath):
    """Open file with default system application."""
    try:
        if sys.platform.startswith('darwin'):  # macOS
            subprocess.run(['open', filepath])
        elif sys.platform.startswith('linux'):  # Linux
            subprocess.run(['xdg-open', filepath])
        elif sys.platform.startswith('win'):  # Windows
            os.startfile(filepath)
        else:
            print(f"Please manually open: {filepath}")
    except Exception as e:
        print(f"Error opening {filepath}: {e}")

def main():
    """Open all diagram files."""
    diagrams = [
        "01_rag_system_overview.png",
        "02_detailed_data_flow.png", 
        "03_component_architecture.png"
    ]
    
    print("🖼️  Opening AWS Architecture Diagrams...")
    
    for diagram in diagrams:
        if os.path.exists(diagram):
            print(f"📊 Opening: {diagram}")
            open_file(diagram)
        else:
            print(f"❌ Not found: {diagram}")
    
    print("✅ All available diagrams opened!")

if __name__ == "__main__":
    main()