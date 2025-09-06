from apscheduler.schedulers.blocking import BlockingScheduler
import requests, os
API = os.getenv("API_URL", "http://api:8000")
sched = BlockingScheduler()
@sched.scheduled_job('cron', hour=1)
def nightly_sync():
    # Example: refresh AAPL daily
    try:
        requests.post(f"{API}/data/sync/prices",params={"symbol":"AAPL","start":"2018-01-01","end":"2025-01-01"}, timeout=30)
    except Exception:
        pass
if __name__ == "__main__":
    sched.start()