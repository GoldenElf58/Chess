import shutil
from pathlib import Path

def remove_cpython_files(path: Path) -> None:
    """
    Remove all files ending with .cpython-313-darwin.so in the given path recursively.
    """
    if not path.exists():
        return
    for file in path.rglob('*.cpython-313-darwin.so'):
        try:
            file.unlink()
            print(f"Removed: {file}")
        except Exception as e:
            print(f"Error removing {file}: {e}")


def clean_build_dir(build_dir: Path) -> None:
    """
    Delete all files and folders in build_dir that are not .py files.
    """
    if not build_dir.exists():
        return
    for item in build_dir.iterdir():
        try:
            if item.is_dir():
                shutil.rmtree(item)
                print(f"Removed directory: {item}")
            elif item.is_file() and item.suffix != '.py':
                item.unlink()
                print(f"Removed file: {item}")
        except Exception as e:
            print(f"Error removing {item}: {e}")


def main() -> None:
    # Base directories
    current_dir = Path(__file__).parent.resolve()
    dirs_to_clean = [
        current_dir,
        current_dir / 'bots',
        current_dir / 'game_states',
    ]

    # Remove .cpython-313-darwin.so files
    for d in dirs_to_clean:
        remove_cpython_files(d)

    # Clean build directory
    build_dir = current_dir / 'build'
    clean_build_dir(build_dir)

if __name__ == '__main__':
    main()

