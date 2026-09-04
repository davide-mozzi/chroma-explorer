import json
import os
from importlib.metadata import version
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any, Literal

import pandas as pd
import streamlit as st
from chromadb import Include, PersistentClient
from chromadb.api import ClientAPI

from chroma_explorer.chroma import (
    create_collection,
    create_vector_store,
    delete_collection,
    get_collection_names,
    rename_collection,
)
from chroma_explorer.errors import (
    EmptyDirectoryError,
    InvalidPathError,
    MissingPathError,
    NonExistentPathError,
)
from chroma_explorer.settings import edit_settings, get_settings


@st.cache_resource
def get_chroma_client(chroma_path: str | None, refresh_count: int) -> ClientAPI:
    if chroma_path:
        settings = edit_settings(path=chroma_path)
    else:
        settings = get_settings()

    if not settings.path:
        st.session_state["chroma_path"] = ""
        raise MissingPathError("missing path to local Chroma directory")

    path = Path(settings.path).expanduser()
    st.session_state["chroma_path"] = str(path)

    if not path.exists():
        if not path.parent.exists():
            raise InvalidPathError("parent path does not exist")

        raise NonExistentPathError("given path does not exist")

    if path.is_dir():
        if not os.listdir(path):
            raise EmptyDirectoryError("given path points to an empty directory")

        if not (path / "chroma.sqlite3").exists():
            raise InvalidPathError("given path does not contain a ChromaDB instance")

    return PersistentClient(path)


@st.dialog(title="Settings", on_dismiss="rerun")
def settings_dialog(path_status: Literal["empty", "invalid", "valid"] = "valid") -> None:
    previous_path = st.session_state.get("chroma_path")
    path = st.text_input(label="ChromaDB path", value=previous_path)

    if path != previous_path:
        st.session_state["chroma_path"] = path
        st.rerun()

    if path:
        if path_status == "invalid":
            st.error(title="Invalid path", body="The given path does not point to a valid directory.")
        elif path_status == "empty":
            st.warning(
                title="Empty directory",
                body="The given path points to an empty or non-existent directory. If you want you can create an empty "
                "ChromaDB vectorstore there.",
            )
            if st.button(label="Create an empty vector store", type="primary"):
                create_vector_store(path)
                st.rerun()


st.set_page_config(layout="wide", initial_sidebar_state=350)
logo = files("chroma_explorer").joinpath("assets/logo.png")
logo_icon = files("chroma_explorer").joinpath("assets/logo_icon.png")

with as_file(logo) as logo_path, as_file(logo_icon) as logo_icon_path:
    st.logo(image=logo_path, icon_image=logo_icon_path, size="large")

with st.bottom, st.container(horizontal=True, horizontal_alignment="center"):
    st.caption(f"Chroma Explorer \u00b7 Version {version('chroma-explorer')}", width="content")

try:
    st.session_state.client = get_chroma_client(
        st.session_state.get("chroma_path"), st.session_state.get("refresh_chroma", 0)
    )
except (EmptyDirectoryError, NonExistentPathError):
    settings_dialog("empty")
    st.stop()
except (InvalidPathError, MissingPathError):
    settings_dialog("invalid")
    st.stop()

with st.sidebar:
    if st.button("Settings", type="tertiary", icon=":material/settings:"):
        settings_dialog()

    with st.expander(label="Create a collection", type="compact"), st.form(key="create_collection"):
        st.subheader(body="Create a collection", anchor=False)
        st.text_input(label="Name", key="create_collection__name")
        st.form_submit_button(label="Create", on_click=create_collection)

    with st.container(border=True):
        st.subheader(body="Select a collection", anchor=False)
        selected_collection = st.selectbox(
            label="Name",
            options=get_collection_names(),
            index=None,
            key="selected_collection",
        )

    include: Include | None = None

    if selected_collection:
        with st.container(border=True):
            with st.form("chroma_get_form", border=False):
                st.subheader("Explore data", anchor=False)
                ids_text = st.text_input("IDs", placeholder="id_1, id_2, id_3")
                where_text = st.text_area("Metadata filter (`where`)", value="", placeholder='{"category": "news"}')
                where_document_text = st.text_area(
                    "Document filter (`where_document`)",
                    value="",
                    placeholder='{"$contains": "python"}',
                )
                include = st.multiselect(
                    "Include",
                    options=["documents", "metadatas", "embeddings"],
                    default=["documents", "metadatas"],
                )
                limit = st.number_input("Limit", min_value=1, value=100, step=1)
                offset = st.number_input("Offset", min_value=0, value=0, step=1)

                if st.form_submit_button("Load data", width="stretch"):
                    try:
                        ids = [item.strip() for item in ids_text.split(",") if item.strip()] or None
                        where = json.loads(where_text) if where_text.strip() else None
                        where_document = json.loads(where_document_text) if where_document_text.strip() else None
                        st.session_state["data"] = st.session_state.client.get_collection(selected_collection).get(
                            ids=ids,
                            where=where,
                            where_document=where_document,
                            include=include,
                            limit=int(limit),
                            offset=int(offset),
                        )
                    except json.JSONDecodeError as exc:
                        st.error(f"Invalid JSON filter: {exc}")

            if st.button("Clear results", type="tertiary", width="stretch"):
                st.session_state["data"] = None


if selected_collection:
    with st.container(horizontal=True, vertical_alignment="center"):
        st.subheader(body=f"Collection: `{selected_collection}`", anchor=False, width="content")

        with (
            st.popover(label="Rename", icon=":material/edit:", width=100, type="tertiary"),
            st.form(key="rename_collection", border=False),
        ):
            st.text_input(label="New name", key="rename_collection__new_name")
            st.form_submit_button(label="Rename", width="stretch", on_click=rename_collection)

        with (
            st.popover(label="Delete", icon=":material/delete:", width=100, type="tertiary"),
            st.form(key="delete_collection", border=False),
        ):
            st.warning(title="Are you sure??", body="Deleting a collection is **irreversible**!")
            st.form_submit_button(label="Delete", type="primary", width="stretch", on_click=delete_collection)

    document_count_text = f"Total documents: {st.session_state.client.get_collection(selected_collection).count()}" + (
        f" \u00b7 Filtered documents: {len(d['ids'])}" if (d := st.session_state.get("data")) else ""
    )
    st.caption(document_count_text, width="content")

    if (data := st.session_state.get("data")) and include:
        rows = []

        for i, record_id in enumerate(data["ids"]):
            row: dict[str, Any] = {"id": record_id}

            for field in include:
                values = data.get(field)

                if values is not None:
                    value = values[i]

                    if field == "metadatas" and value is not None:
                        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
                    elif field == "embeddings" and value is not None:
                        value = value.tolist() if hasattr(value, "tolist") else value

                    row[field] = value

            rows.append(row)

        df = pd.DataFrame(rows)
        col1, col2 = st.columns(2)

        with col1:
            dataframe_state = st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                column_config={field: field.removesuffix("s").capitalize() for field in include} | {"id": "ID"},
                selection_mode="single-row",
                on_select="rerun",
            )

        with col2:
            if len(dataframe_state.selection.rows) > 0:
                selected_doc_data = df.iloc[dataframe_state.selection.rows[0]]

                st.header(f"Document `{selected_doc_data['id']}`", anchor=False)

                if "metadatas" in selected_doc_data:
                    with st.expander(label="Metadata"):
                        st.json(body=selected_doc_data["metadatas"])

                if "documents" in selected_doc_data:
                    with st.container(border=True):
                        st.markdown(body=selected_doc_data["documents"])
else:
    st.markdown(body="No collection selected", help="Please select a collection in the sidebar")
