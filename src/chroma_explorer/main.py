import logging
import sys
from pathlib import Path

from pydantic import PydanticImportError
from streamlit.web import cli

from .settings import get_settings


def run() -> None:
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger("chroma-explorer")
    logger.setLevel(logging.INFO)

    try:
        get_settings()
    except PydanticImportError as e:
        logger.error(e)
        sys.exit(1)

    app_path = Path(__file__).with_name("app.py")
    sys.argv = ["streamlit", "run", str(app_path), "--", *sys.argv[1:]]
    sys.exit(cli.main())
