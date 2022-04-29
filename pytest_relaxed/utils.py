try:
    from pytest import version_tuple as pytest_version_info
except ImportError:
    from pytest import __version__ as pytest_version
    pytest_version_info = tuple(map(int, pytest_version.split(".")[:3]))
