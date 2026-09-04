# Chroma Explorer

Chroma Explorer is a Streamlit application for browsing and managing a local ChromaDB vector store.

## Usage

### Install from source

Clone this repository, then install the application from the project root:

```bash
uv tool install .
```

### Install from a GitHub Release

Download the `.whl` asset from a published GitHub Release, then install it locally:

```bash
uv tool install /path/to/chroma_explorer-<version>-py3-none-any.whl
```

Alternatively, install the wheel directly from its release URL:

```bash
uv tool install \
  https://github.com/davide-mozzi/chroma-explorer/releases/download/<tag>/chroma_explorer-<version>-py3-none-any.whl
```

### Launch

Launch it by providing the path to your local ChromaDB directory:

```bash
chroma-explorer /path/to/chroma-db
```

If a browser does not open automatically (as can happen with WSL), open [http://localhost:8501](http://localhost:8501)
manually.
