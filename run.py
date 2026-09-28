import sys
import os

# Ensure project root is on path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.main import main

if __name__ == "__main__":
    main()
