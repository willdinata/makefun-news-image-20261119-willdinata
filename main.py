#!/usr/bin/env python3
"""
Copy entry.png to MAKEFUN_OUTPUT_DIR (default /output), verify the 8-byte PNG signature,
and print the copied file size and the first 12 hex characters of its SHA256 checksum.
"""

import os
import shutil
import hashlib

def main():
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_image = os.path.join(script_dir, "entry.png")
    dst_image = os.path.join(output_dir, "entry.png")
    
    if not os.path.exists(src_image):
        raise FileNotFoundError(f"Source image not found: {src_image}")
    
    shutil.copyfile(src_image, dst_image)
    
    # Read back destination file and verify PNG signature
    png_signature = b'\x89PNG\r\n\x1a\n'
    with open(dst_image, "rb") as f:
        header = f.read(8)
        if header != png_signature:
            raise ValueError(f"Invalid PNG signature in copied file: {header!r}")
        
        # Read full content for sha256 and size
        f.seek(0)
        data = f.read()
        file_size = len(data)
        
    sha256_hash = hashlib.sha256(data).hexdigest()
    short_sha = sha256_hash[:12]
    
    print(f"Copied size: {file_size} bytes")
    print(f"SHA256 (first 12 hex): {short_sha}")

if __name__ == "__main__":
    main()
