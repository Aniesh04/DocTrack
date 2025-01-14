import streamlit as st
import tempfile
import requests
import pandas as pd
import json

# Set up Streamlit page configuration
st.set_page_config(page_title="DocTrack", layout="wide")
st.title("DocTrack")
st.markdown("<h5><i>Track your document status in seconds</i></h5>", unsafe_allow_html=True)
st.divider()

# Initialize session state variables if not already set
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None

if "dataframe" not in st.session_state:
    st.session_state.dataframe = None

if "uptodate_count" not in st.session_state:
    st.session_state.uptodate_count = 0

if "overdue_count" not in st.session_state:
    st.session_state.overdue_count = 0

if "expiring_soon_count" not in st.session_state:
    st.session_state.expiring_soon_count = 0

# File upload functionality
uploaded_files = st.file_uploader(label="Upload Documents", accept_multiple_files=True)
sub_btn = st.button("Submit")
st.divider()
# Submit button to process files and display results
if sub_btn:
    
    files_to_upload = []

    for uploaded_file in uploaded_files:
        files_to_upload.append(
            ("files", (uploaded_file.name, uploaded_file.read(), uploaded_file.type))
        )

    # Process files via the API
    process_response = requests.post(
        "http://127.0.0.1:8000/process-multiple-files",
        files=files_to_upload
    )

    if process_response.status_code == 200:
        st.success("Files processed successfully!")
        processed_data = process_response.json()
        st.session_state.processed_data = processed_data

        # Retrieve the DataFrame from the backend
        df_response = requests.post(
            "http://127.0.0.1:8000/get-df", 
            json=processed_data  # Pass processed file paths from the backend
        )
        
        if df_response.status_code == 200:
            df = pd.DataFrame(df_response.json())

            # Update counts based on the DataFrame
            uptodate_count = df['Status'].apply(lambda x: x == "Up-to-date").sum()
            overdue_count = df['Status'].apply(lambda x: x == "Overdue").sum()
            expiring_soon_count = df['Status'].apply(lambda x: x == "Expiring soon").sum()

            # Save the DataFrame and counts to session state
            st.session_state.dataframe = df
            st.session_state.uptodate_count = uptodate_count
            st.session_state.overdue_count = overdue_count
            st.session_state.expiring_soon_count = expiring_soon_count

        else:
            st.error(f"Failed to retrieve dataframe: {df_response.content.decode('utf-8')}")
    else:
        st.error(f"File processing failed: {process_response.content.decode('utf-8')}")

# Display metrics and table if data is available
if st.session_state.dataframe is not None:
    df = st.session_state.dataframe
    
    if df.empty:
        st.warning("No records available.")
        uptodate_count = 0
        overdue_count = 0
        expiring_soon_count = 0
    elif 'Status' not in df.columns:
        st.warning("The 'Status' column is missing in the DataFrame.")
        uptodate_count = 0
        overdue_count = 0
        expiring_soon_count = 0
    else:
        uptodate_count = df['Status'].apply(lambda x: x == "Up-to-date").sum()
        overdue_count = df['Status'].apply(lambda x: x == "Overdue").sum()
        expiring_soon_count = df['Status'].apply(lambda x: x == "Expiring soon").sum()


    # uptodate_count = df['Status'].apply(lambda x: x == "Up-to-date").sum()
    # overdue_count = df['Status'].apply(lambda x: x == "Overdue").sum()
    # expiring_soon_count = df['Status'].apply(lambda x: x == "Expiring soon").sum()

    # Display metrics only once and update them when needed
    if "metrics_displayed" not in st.session_state:
        # Display metrics initially
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Up-to-Date", value=uptodate_count)
        col2.metric(label="Overdue", value=overdue_count)
        col3.metric(label="Expiring soon", value=expiring_soon_count)

        # Mark metrics as displayed in session state to prevent duplicate display
        st.session_state.metrics_displayed = True
    else:
        # Update metrics when data changes or when refreshed
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Up-to-Date", value=uptodate_count)
        col2.metric(label="Overdue", value=overdue_count)
        col3.metric(label="Expiring soon", value=expiring_soon_count)

    st.markdown("### Tracking Table")

    # Editable table using st.data_editor
    edited_df = st.data_editor(df)

    # Update session state with the edited dataframe
    st.session_state.dataframe = edited_df

    # Add checkboxes for row selection
    selected_rows = []
    for index, row in df.iterrows():
        checkbox_label = f"Select row {index + 1} (Document: {row['Document name']})"
        is_checked = st.checkbox(checkbox_label, key=f"select_row_{index}")
        if is_checked:
            selected_rows.append(index)

    # Remove selected rows button
    if st.button("Remove Selected Rows"):
        if selected_rows:
            # Remove selected rows from dataframe
            st.session_state.dataframe = st.session_state.dataframe.drop(selected_rows).reset_index(drop=True)

            # Update the counts based on the updated dataframe
            uptodate_count = st.session_state.dataframe['Status'].apply(lambda x: x == "Up-to-date").sum()
            overdue_count = st.session_state.dataframe['Status'].apply(lambda x: x == "Overdue").sum()
            expiring_soon_count = st.session_state.dataframe['Status'].apply(lambda x: x == "Expiring soon").sum()

            # Update session state with the new counts
            st.session_state.uptodate_count = uptodate_count
            st.session_state.overdue_count = overdue_count
            st.session_state.expiring_soon_count = expiring_soon_count

            # Send updated records to backend
            update_response = requests.post(
                "http://127.0.0.1:8000/update-records",
                json=st.session_state.dataframe.to_dict(orient="records"),
            )

            if update_response.status_code == 200:
                st.success("Selected rows removed and database updated!")
            else:
                st.error(f"Failed to update database: {update_response.json()}")
        else:
            st.warning("No rows selected to remove.")

    # Refresh button updates metrics and recalculates counts
    if st.button("Refresh"):
        # Recalculate counts based on the current data
        # uptodate_count = st.session_state.dataframe['Status'].apply(lambda x: x == "Up-to-date").sum()
        # overdue_count = st.session_state.dataframe['Status'].apply(lambda x: x == "Overdue").sum()
        # expiring_soon_count = st.session_state.dataframe['Status'].apply(lambda x: x == "Expiring soon").sum()

        # Update session state and metrics
        st.session_state.uptodate_count = uptodate_count
        st.session_state.overdue_count = overdue_count
        st.session_state.expiring_soon_count = expiring_soon_count

        st.success("Page refreshed!")

    # Clear all rows button
    if st.button("Clear All Rows"):
        # Call the backend to clear the database
        clear_response = requests.post("http://127.0.0.1:8000/clear-database")
        if clear_response.status_code == 200:
            response = clear_response.json()
            if "success" in response:
                # Clear the DataFrame and session state
                # cd = st.session_state.dataframe
                st.session_state.dataframe = pd.DataFrame(data = None, columns=edited_df.columns)  # Reset DataFrame to empty
                st.session_state.uptodate_count = 0
                st.session_state.overdue_count = 0
                st.session_state.expiring_soon_count = 0

                st.success(response["success"])
                edited_df = pd.DataFrame(None)
                df = pd.DataFrame(None)
            else:
                st.error(response.get("error", "Unknown error occurred."))
        else:
            st.error(f"Failed to clear database: {clear_response.content.decode('utf-8')}")

