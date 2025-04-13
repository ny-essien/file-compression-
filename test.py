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

def normalize_path(path: str) -> str:
    """Convert Windows paths to use forward slashes for zip compatibility."""
    return path.replace('\\', '/')

def create_test_files(test_dir: Path):
    """Create test files of different sizes and types."""
    # Create some text files
    (test_dir / "small.txt").write_text("This is a small test file")
    (test_dir / "medium.txt").write_text("This is a medium test file\n" * 1000)
    
    # Create a large file (1MB)
    large_content = "0" * (1024 * 1024)  # 1MB of zeros
    (test_dir / "large.txt").write_text(large_content)
    
    # Create a subdirectory with files
    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "subfile.txt").write_text("File in subdirectory")
    
    logger.info(f"Created test files in {test_dir}")

def run_zip_test(source_dir: Path, output_zip: Path, verify: bool = True):
    """Run the zip_folder.py script with given parameters."""
    cmd = [
        sys.executable,
        "zip_folder.py",
        str(source_dir),
        "--output",
        str(output_zip)
    ]
    
    if verify:
        cmd.append("--verify")
    
    logger.info(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"Command failed with error:\n{result.stderr}")
        return False
    
    logger.info(f"Command output:\n{result.stdout}")
    return True

def verify_zip_contents(zip_path: Path, original_dir: Path):
    """Verify that the zip file contains all original files."""
    import zipfile
    
    # Get list of original files
    original_files = set()
    for root, _, files in os.walk(original_dir):
        for file in files:
            rel_path = Path(root).relative_to(original_dir) / file
            original_files.add(normalize_path(str(rel_path)))
    
    # Get list of files in zip
    zip_files = set()
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zip_files = set(zipf.namelist())
    
    # Compare
    missing_files = original_files - zip_files
    extra_files = zip_files - original_files
    
    if missing_files:
        logger.error(f"Missing files in zip: {missing_files}")
    if extra_files:
        logger.error(f"Extra files in zip: {extra_files}")
    
    return not (missing_files or extra_files)

def main():
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Test case 1: Basic functionality
        logger.info("\n=== Test Case 1: Basic Functionality ===")
        test_dir = temp_path / "test1"
        test_dir.mkdir()
        create_test_files(test_dir)
        
        output_zip = temp_path / "test1.zip"
        if run_zip_test(test_dir, output_zip):
            logger.info("Test Case 1: Basic functionality test passed")
        else:
            logger.error("Test Case 1: Basic functionality test failed")
        
        # Test case 2: Large file handling
        logger.info("\n=== Test Case 2: Large File Handling ===")
        test_dir = temp_path / "test2"
        test_dir.mkdir()
        
        # Create a 10MB file
        large_file = test_dir / "10mb.txt"
        with open(large_file, 'wb') as f:
            f.write(b'0' * (10 * 1024 * 1024))  # 10MB
        
        output_zip = temp_path / "test2.zip"
        if run_zip_test(test_dir, output_zip):
            logger.info("Test Case 2: Large file handling test passed")
        else:
            logger.error("Test Case 2: Large file handling test failed")
        
        # Test case 3: Directory structure preservation
        logger.info("\n=== Test Case 3: Directory Structure ===")
        test_dir = temp_path / "test3"
        test_dir.mkdir()
        
        # Create nested directory structure
        nested = test_dir / "level1" / "level2" / "level3"
        nested.mkdir(parents=True)
        (nested / "deep.txt").write_text("Deep file")
        
        output_zip = temp_path / "test3.zip"
        if run_zip_test(test_dir, output_zip):
            if verify_zip_contents(output_zip, test_dir):
                logger.info("Test Case 3: Directory structure test passed")
            else:
                logger.error("Test Case 3: Directory structure test failed")
        else:
            logger.error("Test Case 3: Directory structure test failed")
        
        # Test case 4: Integrity verification
        logger.info("\n=== Test Case 4: Integrity Verification ===")
        test_dir = temp_path / "test4"
        test_dir.mkdir()
        create_test_files(test_dir)
        
        output_zip = temp_path / "test4.zip"
        if run_zip_test(test_dir, output_zip, verify=True):
            logger.info("Test Case 4: Integrity verification test passed")
        else:
            logger.error("Test Case 4: Integrity verification test failed")

if __name__ == '__main__':
    main() 