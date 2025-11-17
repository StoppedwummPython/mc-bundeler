import requests
import hashlib
import os

def download_and_verify(url, file_path, expected_sha1):
    """
    Downloads a file from a URL, saves it locally,
    and verifies its SHA1 hash.

    Args:
        url (str): The URL of the file to download.
        file_path (str): The local path to save the file.
        expected_sha1 (str): The expected SHA1 hash of the file.

    Returns:
        bool: True if the file is downloaded successfully and the hash matches,
              False otherwise.
    """
    
    if os.path.exists(file_path):
        print(f"File {file_path} already exists. Checking SHA1 hash...")
        print(f"Calculating SHA1 hash for {file_path}...")
        sha1_hash = hashlib.sha1()
        with open(file_path, 'rb') as f:
            # Read the file in chunks to handle large files efficiently
            while chunk := f.read(4096):
                sha1_hash.update(chunk)

        calculated_sha1 = sha1_hash.hexdigest()
        print(f"Calculated SHA1: {calculated_sha1}")
        print(f"Expected SHA1:   {expected_sha1}")

        # Compare the calculated hash with the expected hash
        if calculated_sha1.lower() == expected_sha1.lower():
            print("SHA1 hash verified successfully.")
            return True
        else:
            print("SHA1 hash mismatch.")
            return False
    try:
        # Download the file
        print(f"Downloading {url} to {file_path}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")

        # Calculate the SHA1 hash of the downloaded file
        print(f"Calculating SHA1 hash for {file_path}...")
        sha1_hash = hashlib.sha1()
        with open(file_path, 'rb') as f:
            # Read the file in chunks to handle large files efficiently
            while chunk := f.read(4096):
                sha1_hash.update(chunk)

        calculated_sha1 = sha1_hash.hexdigest()
        print(f"Calculated SHA1: {calculated_sha1}")
        print(f"Expected SHA1:   {expected_sha1}")

        # Compare the calculated hash with the expected hash
        if calculated_sha1.lower() == expected_sha1.lower():
            print("SHA1 hash verified successfully.")
            return True
        else:
            print("SHA1 hash mismatch.")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return False
    except IOError as e:
        print(f"Error handling file: {e}")
        return False
    finally:
        # Clean up the downloaded file if it exists and verification failed
        if 'calculated_sha1' in locals() and calculated_sha1.lower() != expected_sha1.lower() and os.path.exists(file_path):
             os.remove(file_path)
             print(f"Removed invalid file: {file_path}")