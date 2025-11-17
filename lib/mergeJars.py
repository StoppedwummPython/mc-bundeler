# libs/merge.py - A function for in-place merging (advanced, not recommended)
import zipfile
import tqdm

def merge_into_jar(target_jar, source_jars):
    """
    Merges source JARs into a target JAR, modifying it in place.
    """
    print(f"Merging {len(source_jars)} JARs into existing file: {target_jar}...")

    # Open the target JAR in append mode ('a') to add files to it.
    with zipfile.ZipFile(target_jar, 'a', compression=zipfile.ZIP_DEFLATED) as merged_jar:
        # IMPORTANT: We must first populate our set with what's already in the JAR.
        added_files = set(merged_jar.namelist())
        print(f"Target JAR already contains {len(added_files)} files. Skipping duplicates.")

        for source_jar in tqdm.tqdm(source_jars, desc="Processing JARs"):
            try:
                with zipfile.ZipFile(source_jar, 'r') as jar:
                    for file_info in jar.infolist():
                        if file_info.filename not in added_files:
                            content = jar.read(file_info.filename)
                            merged_jar.writestr(file_info, content)
                            added_files.add(file_info.filename)
            except (zipfile.BadZipFile, FileNotFoundError):
                 print(f"Warning: Skipping malformed or missing JAR: {source_jar}")

    print(f"\nFinished merging. Total unique files in {target_jar}: {len(added_files)}")