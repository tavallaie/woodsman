 # Woodsman - A Generic SQL Database Viewer
 
 Inspired by Kino, the anime character known for his formidable weapon, Woodsman lets you navigate and conquer your SQL databases.
 
 ## Overview
 Woodsman is a standalone Python package built with Streamlit that allows you to:
 - Connect to SQL databases (SQLite and PostgreSQL)
 - Reflect the database schema and display available tables
 - Interactively explore table data with filtering and search capabilities
 - Export table data in multiple formats (JSON, CSV, and Markdown)
 
 ## Features
 - **Database Connection:** Choose between SQLite (via file upload or absolute file path) and PostgreSQL.
 - **Schema Reflection:** Automatically list tables available in your connected database.
 - **Data Explorer:** Utilize an interactive data explorer to view and filter table data.
 - **Search Filters:** Apply global or column-specific search filters on the data.
 - **Data Export:** Export filtered data in JSON, CSV, or Markdown format.
 
 ## Installation
 You can install Woodsman using your favorite package manager:
 - With pip: `pip install woodsman`
 - With Poetry: `poetry add woodsman`
 - With uv: `uv add woodsman`
 
 ## Usage
 To run Woodsman, simply execute:
 - With uv: `uv run woodsman`
 - Or, if installed via pip, run it using in your .venv :
   `woodsman`
 
 ## How It Works
 - **SQLite Connection:** Choose between uploading a file or providing an absolute file path.
 - **PostgreSQL Connection:** Input your connection details to connect to a PostgreSQL database.
 - **Table Selection:** Once connected, the app reflects the schema and displays available tables in the sidebar.
 - **Data Exploration:** Select a table to view its data, apply search filters, and interact with the data using the built-in data explorer.
 - **Export Options:** Filtered data can be exported in JSON, CSV, or Markdown formats.
 
## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you have any suggestions or improvements.

 
 ## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
 
 ## Credits
 Developed by Ali Tavallaie. Inspired by Kino, the anime character whose weapon symbolizes power and precision—just like Woodsman, our tool for conquering SQL databases.
