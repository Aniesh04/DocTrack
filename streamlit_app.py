import streamlit as st
import tempfile
import requests
import pandas as pd
import json

st.set_page_config(page_title="DocTrack", layout="wide",)
st.title("DocTrack",)
st.markdown("<h5><i>Track your document status in seconds</i></h5>",unsafe_allow_html=True)
st.divider()

if "processed_data" not in st.session_state:
    st.session_state.processed_data = None

if "dataframe" not in st.session_state:
    st.session_state.dataframe = None


uploaded_files = st.file_uploader(label="Upload Documents",accept_multiple_files=True)

if st.button("Submit"):
    files_to_upload = []
    filepaths = []

    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as temp_file:
            temp_file.write(uploaded_file.read())
            filepaths.append(temp_file.name)
            files_to_upload.append(("files", (uploaded_file.name, open(temp_file.name, "rb"), uploaded_file.type)))

    process_response = requests.post("http://127.0.0.1:8000/process-multiple-files", files=files_to_upload)

    if process_response.status_code == 200:
        st.success("Files processed successfully!")
        processed_data = process_response.json()
        st.write(processed_data)

        # Save processed data in session state
        st.session_state.processed_data = processed_data

        df_response = requests.post("http://127.0.0.1:8000/get-df", json=filepaths)

        if df_response.status_code == 200:
            df = pd.DataFrame(df_response.json())
            uptodate_count = df['Status'].apply(lambda x: x == "Up-to-date").sum()
            overdue_count = df['Status'].apply(lambda x: x == "Overdue").sum()
            expiring_soon_count = df['Status'].apply(lambda x: x == "Expiring soon").sum()
            # st.markdown()
            # st.data_editor(df)

            # Save dataframe in session state
            st.session_state.dataframe = df
        else:
            st.error(f"Failed to retrieve dataframe: {df_response.content.decode('utf-8')}")
    else:
        st.error(f"File processing failed: {process_response.content.decode('utf-8')}")

    clear_btn = st.button("clear")
    if clear_btn:
        st.session_state.dataframe = None
    
    col1, col2, col3 = st.columns(3,border=True)
    col1.metric(label="Up-to-Date", value=uptodate_count)
    col2.metric(label="Overdue", value=overdue_count)
    col3.metric(label="expiring soon",value=expiring_soon_count)

if st.session_state.dataframe is not None:
    st.markdown("### Tracking Table")
    edited_df = st.data_editor(st.session_state.dataframe, key="data_editor",use_container_width=True)

    # Update the session state dataframe with edits
    if edited_df is not None:
        st.session_state.dataframe = edited_df

