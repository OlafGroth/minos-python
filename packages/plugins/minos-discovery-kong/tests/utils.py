from pathlib import (
    Path,
)

BASE_PATH = Path(__file__).parent
CONFIG_FILE_PATH = BASE_PATH / "test_config.yml"
rand = 27
TEST_HOST = f"{rand}.{rand}.{rand}.{rand}"
