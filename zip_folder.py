import os
import sys
import zipfile
import hashlib
import logging
import argparse
import tempfile
from pathlib import Path
from typing import Dict, Tuple, Optional
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('zipping.log')
    ]
)
logger = logging.getLogger(__name__)

# Constants
CHUNK_SIZE = 64 * 1024 * 1024  # 64MB chunks for memory efficiency

def compute_file_hash(file_path: Path, chunk_size: int = CHUNK_SIZE) -> Optional[str]:
    """
    Compute SHA-256 hash of a file in chunks to be memory efficient.
    Returns None if file cannot be read.
    """
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except (IOError, OSError) as e:
        logger.warning(f"Could not read file {file_path}: {str(e)}")
        return None

def normalize_path(path: str) -> str:
    """Convert Windows paths to use forward slashes for zip compatibility."""
    return path.replace('\\', '/')

def zip_folder(
    source_folder: Path,
    output_zip: Path,
    hash_log: Path
) -> Tuple[bool, Dict[str, str]]:
    """
    Zip a folder with no compression, maintaining file hashes.
    Returns success status and dictionary of file hashes.
    """
    file_hashes = {}
    success = True

    try:
        with zipfile.ZipFile(
            output_zip,
            'w',
            compression=zipfile.ZIP_STORED,
            allowZip64=True
        ) as zipf:
            # Walk through the directory
            for root, _, files in os.walk(source_folder):
                for file in tqdm(files, desc="Zipping files"):
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(source_folder)
                    zip_path = normalize_path(str(rel_path))

                    try:
                        # Compute hash before zipping
                        file_hash = compute_file_hash(file_path)
                        if file_hash is None:
                            success = False
                            continue

                        file_hashes[zip_path] = file_hash

                        # Add file to zip
                        zipf.write(file_path, zip_path)
                        logger.info(f"Added {zip_path} to zip")

                    except (IOError, OSError) as e:
                        logger.error(f"Error processing {file_path}: {str(e)}")
                        success = False

        # Save hashes to log file
        with open(hash_log, 'w') as f:
            for file_path, file_hash in file_hashes.items():
                f.write(f"{file_path}:{file_hash}\n")

        return success, file_hashes

    except Exception as e:
        logger.error(f"Error creating zip file: {str(e)}")
        return False, {}

def verify_integrity(
    zip_path: Path,
    hash_log: Path,
    temp_dir: Optional[Path] = None
) -> bool:
    """
    Verify the integrity of zipped files by comparing hashes.
    """
    try:
        # Read original hashes
        original_hashes = {}
        with open(hash_log, 'r') as f:
            for line in f:
                file_path, file_hash = line.strip().split(':')
                original_hashes[file_path] = file_hash

        # Create temporary directory if not provided
        if temp_dir is None:
            temp_dir = Path(tempfile.mkdtemp())

        # Extract and verify each file
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            for file_path in tqdm(original_hashes.keys(), desc="Verifying files"):
                try:
                    # Extract file
                    extracted_path = temp_dir / file_path
                    extracted_path.parent.mkdir(parents=True, exist_ok=True)
                    zipf.extract(file_path, temp_dir)

                    # Compute hash of extracted file
                    extracted_hash = compute_file_hash(extracted_path)
                    if extracted_hash is None:
                        return False

                    # Compare hashes
                    if extracted_hash != original_hashes[file_path]:
                        logger.error(f"Hash mismatch for {file_path}")
                        return False

                except Exception as e:
                    logger.error(f"Error verifying {file_path}: {str(e)}")
                    return False

        return True

    except Exception as e:
        logger.error(f"Error during integrity verification: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Zip a folder with no compression and verify integrity')
    parser.add_argument('source_folder', type=Path, help='Source folder to zip')
    parser.add_argument('--output', type=Path, help='Output zip file path (default: source_folder.zip)')
    parser.add_argument('--verify', action='store_true', help='Verify integrity after zipping')
    
    args = parser.parse_args()

    # Set default output path if not provided
    if args.output is None:
        args.output = args.source_folder.with_suffix('.zip')

    # Ensure source folder exists
    if not args.source_folder.exists() or not args.source_folder.is_dir():
        logger.error(f"Source folder {args.source_folder} does not exist or is not a directory")
        sys.exit(1)

    # Create hash log path
    hash_log = args.output.with_suffix('.hash')

    # Zip the folder
    logger.info(f"Starting to zip {args.source_folder}")
    success, file_hashes = zip_folder(args.source_folder, args.output, hash_log)

    if not success:
        logger.error("Some files could not be processed during zipping")
        sys.exit(1)

    logger.info(f"Successfully created zip file: {args.output}")

    # Verify integrity if requested
    if args.verify:
        logger.info("Starting integrity verification")
        if verify_integrity(args.output, hash_log):
            logger.info("Integrity verification successful")
        else:
            logger.error("Integrity verification failed")
            sys.exit(1)

if __name__ == '__main__':
    main() 