"""
Background health check and keep-alive service for Streamlit applications.
Pings internal Streamlit health endpoints and external public URLs periodically
to prevent cloud hosting providers (e.g. Streamlit Community Cloud) from putting
the app to sleep due to inactivity.
"""

import threading
import time
import os
import logging
import requests
import streamlit as st

logger = logging.getLogger("health_check")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [HealthCheck] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

_health_check_started = False
_lock = threading.Lock()


def _run_health_check_loop(interval_seconds: int = 60, public_url: str | None = None):
    """
    Background daemon loop that periodically pings:
    1. Local Streamlit health endpoint (http://127.0.0.1:{port}/_stcore/health)
    2. External public URL (to register incoming edge traffic on Streamlit Cloud)
    """
    port = os.getenv("PORT", os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    local_url = f"http://127.0.0.1:{port}/_stcore/health"
    target_url = public_url or os.getenv(
        "APP_URL",
        os.getenv("STREAMLIT_APP_URL", "https://meeting-assistant-mom.streamlit.app")
    )

    logger.info(
        f"Health check daemon started (interval: {interval_seconds}s, "
        f"local: {local_url}, target: {target_url})"
    )

    # Initial grace period allowing the Streamlit server to bind and start
    time.sleep(min(15, interval_seconds))

    while True:
        # 1. Ping local Streamlit health endpoint
        try:
            res_local = requests.get(local_url, timeout=5)
            if res_local.status_code == 200:
                logger.info(f"Local health check OK (status: {res_local.status_code})")
            else:
                logger.warning(f"Local health check returned status: {res_local.status_code}")
        except Exception as e:
            logger.debug(f"Local health check ping failed: {e}")

        # 2. Ping external public URL to keep Streamlit Cloud edge awake
        if target_url:
            try:
                headers = {"User-Agent": "MOM-Streamlit-HealthCheck/1.0"}
                res_ext = requests.get(
                    target_url,
                    headers=headers,
                    allow_redirects=True,
                    timeout=10
                )
                logger.info(
                    f"Keep-alive ping to {target_url} succeeded (status: {res_ext.status_code})"
                )
            except Exception as e:
                logger.warning(f"Keep-alive ping to {target_url} failed: {e}")

        time.sleep(interval_seconds)


@st.cache_resource
def start_background_health_check(
    interval_seconds: int = 60,
    public_url: str | None = None
) -> bool:
    """
    Starts the background health check daemon thread.
    Protected with @st.cache_resource and a threading lock to ensure
    only a single worker instance runs across all Streamlit sessions and reruns.
    """
    global _health_check_started
    with _lock:
        if not _health_check_started:
            thread = threading.Thread(
                target=_run_health_check_loop,
                args=(interval_seconds, public_url),
                daemon=True,
                name="MOM-HealthCheck-Daemon",
            )
            thread.start()
            _health_check_started = True
            logger.info("Background health check daemon thread initialized successfully.")
    return True
