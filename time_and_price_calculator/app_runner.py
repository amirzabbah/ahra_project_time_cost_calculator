import subprocess
# from .configs.config_reader import PORT


def run():
    """
    Run a Streamlit app on a specified port using a subprocess.

    This function runs the Streamlit app located at `/app/comment_checker/streamlit_app_assets.py` on the port specified
    by the `COMMENT_CHECKER_PANEL_PORT` environment variable, using a subprocess. The function does not return anything.

    Raises
    ------
    subprocess.CalledProcessError
        If the subprocess exits with a non-zero return code.

    Examples
    --------
    >>> run()  # runs the Streamlit app on the specified port

    """
    # command = f'python -m streamlit run ./data_quality_report_panel/app.py --server.port {PORT}'
    command = f'python -m streamlit run ./time_and_price_calculator/app.py'

    # Run the command and capture the output
    subprocess.run(command, shell=True)
