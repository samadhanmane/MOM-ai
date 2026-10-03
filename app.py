"""
app.py
======
Entry point compatibility wrapper for Streamlit Community Cloud.
Dispatches execution directly to streamlit_app.py.
"""
import os
import runpy

entry_point = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'streamlit_app.py')
runpy.run_path(entry_point, run_name='__main__')
