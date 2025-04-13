#!/usr/bin/env python3
import os
import sys
import shutil
import tempfile
import subprocess
import argparse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_specific_path(input_path: Path, verify: bool = True):
    """
    Test zip_folder.py with a specific file or folder.
    If input is a file, it will be placed in a temporary directory first.
    """
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        if input_path.is_file():
            # If input is a file, create a directory and move the file into it
            test_dir = temp_path / "test_folder"
            test_dir.mkdir()
            shutil.copy2(input_path, test_dir / input_path.name)
            source_path = test_dir
        else:
            # If input is a directory, use it directly
            source_path = input_path
        
        # Set output path
        output_zip = temp_path / f"{input_path.stem}.zip"
        
        # Build command
        cmd = [
            sys.executable,
            "zip_folder.py",
            str(source_path),
            "--output",
            str(output_zip)
        ]
        
        if verify:
            cmd.append("--verify")
        
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Test successful!")
            logger.info(f"Created zip file: {output_zip}")
            logger.info(f"Created hash file: {output_zip.with_suffix('.hash')}")
            
            # Copy results to current directory for inspection
            final_zip = Path.cwd() / f"{input_path.stem}_test.zip"
            final_hash = Path.cwd() / f"{input_path.stem}_test.hash"
            
            shutil.copy2(output_zip, final_zip)
            shutil.copy2(output_zip.with_suffix('.hash'), final_hash)
            
            logger.info(f"Copied results to current directory:")
            logger.info(f"  - Zip file: {final_zip}")
            logger.info(f"  - Hash file: {final_hash}")
        else:
            logger.error("Test failed!")
            logger.error(f"Error output:\n{result.stderr}")

def main():
    parser = argparse.ArgumentParser(description='Test zip_folder.py with a specific file or folder')
    parser.add_argument('path', type=Path, help='Path to the file or folder to test')
    parser.add_argument('--no-verify', action='store_true', help='Skip integrity verification')
    
    args = parser.parse_args()
    
    if not args.path.exists():
        logger.error(f"Path does not exist: {args.path}")
        sys.exit(1)
    
    test_specific_path(args.path, verify=not args.no_verify)

if __name__ == '__main__':
    main() 