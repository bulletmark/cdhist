import sys
from pathlib import Path

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

def Version():
    pkg = Path(sys.argv[0]).stem.replace('_', '-')
    try:
        version = metadata.version(pkg)
    except Exception:
        version = '?'

    return version
