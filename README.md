# Zip Folder Utility

A Python utility for creating uncompressed zip archives with integrity verification. This tool is designed to handle large files efficiently while maintaining data integrity through SHA-256 hashing.

## Features

- 🚀 **Efficient Large File Handling**: Optimized for files up to 20GB
- 💾 **No Compression**: Uses store mode (no compression) for maximum speed
- 🔒 **Data Integrity**: SHA-256 hash verification
- 📝 **Detailed Logging**: Comprehensive operation logs
- 🖥️ **CLI Interface**: Easy command-line usage
- 🧪 **Test Suite**: Built-in testing capabilities

## Requirements

- Python 3.6 or higher
- Dependencies:
  - tqdm (for progress bars)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd zip-folder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Zip a folder:
```bash
python zip_folder.py path/to/your/folder
```

### Advanced Options

1. **Custom Output Name**:
```bash
python zip_folder.py path/to/your/folder --output custom_name.zip
```

2. **With Integrity Verification**:
```bash
python zip_folder.py path/to/your/folder --verify
```

3. **Both Custom Output and Verification**:
```bash
python zip_folder.py path/to/your/folder --output custom_name.zip --verify
```

## Testing

### Running Tests

1. **Comprehensive Test Suite**:
```bash
python test.py
```
This runs all test cases including:
- Basic functionality
- Large file handling
- Directory structure preservation
- Integrity verification

2. **Test Specific File/Folder**:
```bash
python test_specific_file.py path/to/your/file_or_folder
```

3. **Test Without Verification**:
```bash
python test_specific_file.py path/to/your/file_or_folder --no-verify
```

## Output Files

The utility creates the following files:

1. **Zip Archive**:
   - Default: `[folder_name].zip`
   - Custom: `[specified_name].zip`

2. **Hash File**:
   - Contains SHA-256 hashes of all files
   - Format: `[zip_name].hash`

3. **Log File**:
   - Detailed operation logs
   - Format: `zipping.log`

## Technical Details

### Memory Efficiency

- Uses 64MB chunks for file processing
- Streams files instead of loading into memory
- Suitable for systems with 16GB RAM

### Path Handling

- Normalizes paths to use forward slashes
- Preserves directory structure
- Handles Windows paths correctly

### Error Handling

- Skips unreadable files with warnings
- Provides detailed error messages
- Graceful handling of large files

## Example Output

```
2023-04-13 14:21:11,585 - INFO - Starting to zip /path/to/folder
2023-04-13 14:21:13,534 - INFO - Added file1.txt to zip
2023-04-13 14:21:13,537 - INFO - Successfully created zip file: folder.zip
2023-04-13 14:21:13,537 - INFO - Starting integrity verification
2023-04-13 14:21:13,881 - INFO - Integrity verification successful
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and feature requests, please use the GitHub issue tracker. 