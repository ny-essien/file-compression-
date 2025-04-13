#!/usr/bin/env python3
import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_single_file():
    """Test zip_folder.py with a single file."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a test file
        test_file = temp_path / "test.txt"
        test_file.write_text("This is a test file for zip_folder.py")
        
        # Create a directory to put the file in (since zip_folder.py works with directories)
        test_dir = temp_path / "test_folder"
        test_dir.mkdir()
        
        # Move the file into the directory
        shutil.move(test_file, test_dir / "test.txt")
        
        # Run zip_folder.py
        output_zip = temp_path / "test.zip"
        cmd = [
            sys.executable,
            "zip_folder.py",
            str(test_dir),
            "--output",
            str(output_zip),
            "--verify"
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Test successful!")
            logger.info(f"Created zip file: {output_zip}")
            logger.info(f"Created hash file: {output_zip.with_suffix('.hash')}")
        else:
            logger.error("Test failed!")
            logger.error(f"Error output:\n{result.stderr}")

if __name__ == '__main__':
    test_single_file() 