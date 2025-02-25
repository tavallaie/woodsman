import streamlit as st
from sqlalchemy import create_engine, MetaData, text
import pandas as pd
import tempfile
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.dataframe_explorer import dataframe_explorer
import streamlit.web.cli as stcli
import sys
from streamlit import runtime
import warnings

warnings.filterwarnings(
    "ignore",
    message="Could not infer format, so each element will be parsed individually, falling back to `dateutil`",
)


def get_engine(conn_str):
    try:
        engine = create_engine(conn_str)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None


def webui() -> None:
    st.title("Kinoscope")
    st.write("Enter your database connection details below and click **Connect**.")

    colored_header(
        label="Database Connection",
        description="Choose connection type and enter details",
        color_name="blue-70",
    )

    connection_type = st.radio("Connection Type", options=["SQLite", "PostgreSQL"])

    if connection_type == "SQLite":
        sqlite_source = st.radio("SQLite Source", options=["Upload File", "File Path"])
        if sqlite_source == "Upload File":
            uploaded_file = st.file_uploader(
                "Upload SQLite file", type=["db", "sqlite"]
            )
            if uploaded_file is not None:
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".db"
                ) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    sqlite_path = tmp_file.name
                st.info(f"Using temporary file: {sqlite_path}")
                conn_str = f"sqlite:///{sqlite_path}"
            else:
                conn_str = None
        else:
            file_path = st.text_input(
                "SQLite Database File (absolute path)",
                value=st.session_state.get("abs_path", ""),
            )
            if file_path:
                st.session_state["abs_path"] = file_path
                conn_str = f"sqlite:///{file_path}"
            else:
                conn_str = None
    else:
        st.write("Enter PostgreSQL connection details:")
        username = st.text_input("Username", "postgres")
        password = st.text_input("Password", type="password")
        host = st.text_input("Host", "localhost")
        port = st.text_input("Port", "5432")
        database = st.text_input("Database", "mydb")
        conn_str = f"postgresql://{username}:{password}@{host}:{port}/{database}"

    if st.button("Connect"):
        if conn_str is None:
            st.error("Please provide a valid SQLite file or file path.")
        else:
            engine = get_engine(conn_str)
            if engine:
                st.success("Connected successfully!")
                st.session_state.engine = engine
            else:
                st.session_state.engine = None

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
                explored_df = dataframe_explorer(df)
                filtered_df = explored_df.copy()

                st.markdown("### Search Filters")
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
                if search_text:
                    if search_columns:
                        mask = (
                            filtered_df[search_columns]
                            .astype(str)
                            .apply(
                                lambda x: x.str.contains(
                                    search_text, case=False, na=False
                                )
                            )
                            .any(axis=1)
                        )
                    else:
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
                    export_data = filtered_df.to_json(
                        orient="records", force_ascii=False
                    )
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


def run():
    if runtime.exists():
        webui()
    else:
        sys.argv = ["streamlit", "run", __file__, "--theme.base", "dark"] + sys.argv
        sys.exit(stcli.main())


if __name__ == "__main__":
    run()
