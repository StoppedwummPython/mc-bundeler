import os

def make_dir(dir: str):
    try:
        os.mkdir(dir)
    except FileExistsError:
        # It's better to specifically catch FileExistsError
        # if you expect the directory to already be there.
        pass
    except Exception as e:
        # Catch other potential exceptions during directory creation
        print(f"Error creating .build directory: {e}")