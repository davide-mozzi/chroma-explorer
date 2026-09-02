import sys
from pathlib import Path

from streamlit.web import cli


def run() -> None:
    app_path = Path(__file__).with_name("app.py")
    sys.argv = ["streamlit", "run", str(app_path), "--", *sys.argv[1:]]
    sys.exit(cli.main())
