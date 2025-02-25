import streamlit as st
from sqlalchemy import create_engine, MetaData, text
import pandas as pd
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.dataframe_explorer import (
    dataframe_explorer,
)  # Assuming this component is available


# ------------------------------------------------------------------
# Helper: Create SQLAlchemy engine based on connection details
# ------------------------------------------------------------------
def get_engine(conn_str):
    try:
        engine = create_engine(conn_str)
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None


# ------------------------------------------------------------------
# Main Page: Ask for Database Connection Details
# ------------------------------------------------------------------
st.title("Generic SQL Database Viewer")
st.write("Enter your database connection details below and click **Connect**.")

# Use a colored header from streamlit-extras for enhanced UI
colored_header(
    label="Database Connection",
    description="Choose connection type and enter details",
    color_name="blue-70",
)

connection_type = st.radio("Connection Type", options=["SQLite", "PostgreSQL"])

if connection_type == "SQLite":
    sqlite_file = st.text_input("SQLite Database File", "mydatabase.db")
    conn_str = f"sqlite:///{sqlite_file}"
else:
    st.write("Enter PostgreSQL connection details:")
    username = st.text_input("Username", "postgres")
    password = st.text_input("Password", type="password")
    host = st.text_input("Host", "localhost")
    port = st.text_input("Port", "5432")
    database = st.text_input("Database", "mydb")
    conn_str = f"postgresql://{username}:{password}@{host}:{port}/{database}"

if st.button("Connect"):
    engine = get_engine(conn_str)
    if engine:
        st.success("Connected successfully!")
        st.session_state.engine = engine
    else:
        st.session_state.engine = None

# ------------------------------------------------------------------
# If connected, Reflect Schema and Display Tables in Sidebar
# ------------------------------------------------------------------
if "engine" in st.session_state and st.session_state.engine is not None:
    engine = st.session_state.engine

    metadata = MetaData()
    try:
        metadata.reflect(bind=engine)
        table_names = list(metadata.tables.keys())
    except Exception as e:
        st.error(f"Error reflecting database schema: {e}")
        table_names = []

    add_vertical_space(2)
    colored_header(
        label="Tables",
        description="Select a table to view its data",
        color_name="green-70",
    )

    if table_names:
        selected_table = st.sidebar.selectbox("Select a table", table_names)
    else:
        st.sidebar.info("No tables found in the connected database.")
        selected_table = None

    st.write("This app shows the contents of the table you select in the sidebar.")
    if selected_table:
        query = f"SELECT * FROM {selected_table}"
        try:
            df = pd.read_sql_query(text(query), engine)
            st.write(f"**🔭 Data Explorer: {selected_table}**")
            # Use the DataFrame Explorer UI from streamlit-extras
            explored_df = dataframe_explorer(df)

            # Make a copy to apply search filters
            filtered_df = explored_df.copy()

            st.markdown("### Search Filters")
            # Let the widgets manage their own state via keys
            search_text = st.text_input(
                "Enter search text",
                value=st.session_state.get("search_text", ""),
                key="search_text",
            )
            search_columns = st.multiselect(
                "Select columns to filter (leave empty for global search)",
                options=explored_df.columns.tolist(),
                default=st.session_state.get("search_columns", []),
                key="search_columns",
            )

            # Apply filtering based on search parameters
            if search_text:
                if search_columns:
                    # Filter only in the selected columns
                    mask = (
                        filtered_df[search_columns]
                        .astype(str)
                        .apply(
                            lambda x: x.str.contains(search_text, case=False, na=False)
                        )
                        .any(axis=1)
                    )
                else:
                    # Global search: filter across all columns
                    mask = filtered_df.astype(str).apply(
                        lambda row: row.str.contains(
                            search_text, case=False, na=False
                        ).any(),
                        axis=1,
                    )
                filtered_df = filtered_df[mask]

            st.markdown("### Export Data")
            export_format = st.selectbox(
                "Select export format", ["JSON", "CSV", "Markdown"]
            )

            if export_format == "JSON":
                export_data = filtered_df.to_json(orient="records", force_ascii=False)
                mime_type = "application/json"
                file_ext = "json"
            elif export_format == "CSV":
                export_data = filtered_df.to_csv(index=False)
                mime_type = "text/csv"
                file_ext = "csv"
            elif export_format == "Markdown":
                export_data = filtered_df.to_markdown(index=False)
                mime_type = "text/markdown"
                file_ext = "md"

            st.download_button(
                label=f"Download {export_format}",
                data=export_data,
                file_name=f"{selected_table}.{file_ext}",
                mime=mime_type,
            )

            st.write("### Explored Data:")
            st.dataframe(filtered_df)

        except Exception as e:
            st.error(f"Error loading data from table {selected_table}: {e}")
else:
    st.info("Please connect to a database to view its tables.")
