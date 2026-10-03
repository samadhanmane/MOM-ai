"""
MOM AI Video Assistant - Keep-Alive & Wake-Up Service
=====================================================
Performs periodic external GET and POST requests against the hosted Streamlit
application to prevent inactivity hibernation (sleep mode after 10-15 minutes).

Mechanisms:
1. HTTP GET on the root domain (registers visitor page-view traffic at edge router).
2. HTTP GET on '/api/v2/app/status' (inspects platform health and retrieves CSRF tokens).
3. HTTP POST on '/api/v2/app/resume' (triggers official Streamlit Cloud wake-up if sleeping).
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime
from http.cookies import SimpleCookie
import requests

# ── Logging Configuration ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [KeepAlive] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("keep_alive")

DEFAULT_APP_URL = os.getenv(
    "APP_URL",
    os.getenv("STREAMLIT_APP_URL", "https://meeting-assistant-mom.streamlit.app")
).rstrip("/")

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


def ping_and_wake(
    url: str = DEFAULT_APP_URL,
    force_resume: bool = False,
    timeout: int = 20,
) -> dict:
    """
    Executes a keep-alive sequence against the target Streamlit application:
    1. HTTP GET on root application URL (simulates visitor request).
    2. HTTP GET on /api/v2/app/status to verify platform health (0/5 = healthy, 12 = sleeping).
    3. HTTP POST on /api/v2/app/resume with CSRF tokens if sleeping or force_resume=True.

    Returns a diagnostic dictionary.
    """
    clean_url = url.rstrip("/")
    start_time = time.time()
    session = requests.Session()
    session.headers.update(BROWSER_HEADERS)

    result = {
        "url": clean_url,
        "timestamp": datetime.now().isoformat(),
        "get_root_status": None,
        "platform_status_code": None,
        "is_sleeping": False,
        "post_resume_status": None,
        "success": False,
        "latency_sec": 0.0,
        "message": "",
    }

    try:
        # Step 1: Send HTTP GET to public root
        logger.info(f"Step 1/3: Sending HTTP GET to {clean_url} ...")
        res_root = session.get(clean_url, timeout=timeout)
        result["get_root_status"] = res_root.status_code
        logger.info(f"Root URL responded with HTTP {res_root.status_code} ({len(res_root.content)} bytes)")

        # Step 2: Send HTTP GET to /api/v2/app/status
        status_endpoint = f"{clean_url}/api/v2/app/status"
        logger.info(f"Step 2/3: Checking status endpoint {status_endpoint} ...")
        res_status = session.get(status_endpoint, timeout=timeout)
        result["status_api_code"] = res_status.status_code

        csrf_token = res_status.headers.get("x-csrf-token")
        set_cookie_header = res_status.headers.get("set-cookie", "")

        csrf_cookie_val = ""
        if set_cookie_header:
            cookie_parser = SimpleCookie()
            cookie_parser.load(set_cookie_header)
            if "_streamlit_csrf" in cookie_parser:
                csrf_cookie_val = cookie_parser["_streamlit_csrf"].value

        raw_platform_status = None
        if res_status.status_code == 200:
            try:
                payload = res_status.json()
                raw_platform_status = payload.get("status")
                result["platform_status_code"] = raw_platform_status
                logger.info(f"Streamlit Cloud Platform status code: {raw_platform_status}")
            except Exception as json_err:
                logger.debug(f"Status response was not JSON: {json_err}")

        # In Streamlit Cloud, status 12 indicates sleeping / hibernated
        is_sleeping = (raw_platform_status == 12)
        result["is_sleeping"] = is_sleeping

        # Step 3: Wake up / Resume if app is sleeping or proactively requested
        if is_sleeping or force_resume:
            resume_endpoint = f"{clean_url}/api/v2/app/resume"
            reason = "App is in sleep mode (status 12)" if is_sleeping else "Proactive keep-alive wake-up"
            logger.info(f"Step 3/3: {reason}. Sending HTTP POST to {resume_endpoint} ...")

            headers = {}
            if csrf_token:
                headers["x-csrf-token"] = csrf_token

            cookies = {}
            if csrf_cookie_val:
                cookies["_streamlit_csrf"] = csrf_cookie_val

            res_resume = session.post(
                resume_endpoint,
                headers=headers,
                cookies=cookies if cookies else None,
                timeout=timeout,
            )
            result["post_resume_status"] = res_resume.status_code
            logger.info(f"Resume POST request responded with HTTP {res_resume.status_code}")

            if res_resume.status_code in [200, 204]:
                result["success"] = True
                result["message"] = f"App successfully woken up / resumed (HTTP {res_resume.status_code})"
            else:
                result["message"] = f"Resume returned HTTP {res_resume.status_code}"
        else:
            result["success"] = (res_root.status_code == 200)
            result["message"] = f"App is active and healthy (status: {raw_platform_status})"

    except Exception as exc:
        result["message"] = f"Keep-alive request failed: {str(exc)}"
        logger.error(result["message"])

    result["latency_sec"] = round(time.time() - start_time, 2)
    logger.info(f"Keep-alive finished in {result['latency_sec']}s: {result['message']}")
    return result


def run_continuous_daemon(url: str, interval_seconds: int = 300, duration_seconds: int | None = None):
    """
    Runs a continuous keep-alive loop at specified intervals.
    If duration_seconds is given, stops after duration_seconds has elapsed.
    """
    logger.info(
        f"Starting keep-alive continuous loop for {url} every {interval_seconds}s"
        + (f" (duration limit: {duration_seconds}s)" if duration_seconds else " (running indefinitely)")
    )
    start_time = time.time()
    count = 0

    try:
        while True:
            count += 1
            logger.info(f"--- Keep-alive cycle #{count} ---")
            ping_and_wake(url=url, force_resume=False)

            if duration_seconds and (time.time() - start_time >= duration_seconds):
                logger.info(f"Completed scheduled duration of {duration_seconds}s. Exiting cleanly.")
                break

            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        logger.info("Keep-alive daemon stopped by user.")


def main():
    parser = argparse.ArgumentParser(
        description="MOM AI Assistant Streamlit Keep-Alive & Wake-Up Utility"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_APP_URL,
        help="Target Streamlit application URL (default: %(default)s)",
    )
    parser.add_argument(
        "--force-resume",
        action="store_true",
        help="Always send HTTP POST /api/v2/app/resume even if status appears healthy",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run continuously as a background ping loop",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval in seconds between pings when running in daemon mode (default: 300s / 5 mins)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help="Total duration in seconds to keep running before exiting (useful for CI/CD runners)",
    )

    args = parser.parse_args()

    if args.daemon:
        run_continuous_daemon(
            url=args.url,
            interval_seconds=args.interval,
            duration_seconds=args.duration,
        )
    else:
        res = ping_and_wake(url=args.url, force_resume=args.force_resume)
        sys.exit(0 if res.get("success") else 1)


if __name__ == "__main__":
    main()
