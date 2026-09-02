from pathlib import Path

import streamlit as st
from chromadb import PersistentClient
from chromadb.api import ClientAPI


def get_collection_names() -> list[str]:
    client: ClientAPI = st.session_state.client
    return sorted(collection.name for collection in client.list_collections())


def create_vector_store(path: str | Path) -> None:
    PersistentClient(Path(path).expanduser())
    st.session_state["refresh_chroma"] = st.session_state.get("refresh_chroma", 0) + 1


def create_collection() -> None:
    if not (name := st.session_state.get("create_collection__name")):
        return

    client: ClientAPI = st.session_state.client
    client.create_collection(name)
    st.session_state["create_collection__name"] = ""
    st.session_state["selected_collection"] = name


def rename_collection() -> None:
    if not (current_name := st.session_state.get("selected_collection")):
        return

    if not (new_name := st.session_state.get("rename_collection__new_name")):
        return

    client: ClientAPI = st.session_state.client
    collection = client.get_collection(current_name)
    collection.modify(name=new_name)
    st.session_state["rename_collection__new_name"] = ""
    st.session_state["selected_collection"] = new_name


def delete_collection() -> None:
    if not (name := st.session_state.get("selected_collection")):
        return

    client: ClientAPI = st.session_state.client
    client.delete_collection(name)
    st.session_state["selected_collection"] = None
    st.toast(body=f"Collection `{name}` deleted", icon=":material/delete:")
