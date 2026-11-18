# https://stackoverflow.com/questions/11436502/closing-all-threads-with-a-keyboard-interrupt
import time
import requests
import threading
from django.utils import timezone
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from django.db import close_old_connections
from data.models import JudgeWorker
from services.dispatcher import dispatch_task


class Command(BaseCommand):
    help = "Continuously polls judge workers & dispatches from job queue"

    def add_arguments(self, parser):
        parser.add_argument("--hb-int", type=int, default=5)
        parser.add_argument("--fb-int", type=int, default=20)
        parser.add_argument("--fb-times", type=int, default=5)

    def handle(self, *args, **options):
        hb_int = options["hb_int"]
        fb_int = options["fb_int"]
        fb_times = options["fb_times"]
        
        if hb_int <= 0 or fb_int <= 0 or fb_times <= 0:
            print(f"Intervals must be at least 1.")
            return
        
        run_event = threading.Event()
        run_event.set()
        
        thread_hb = threading.Thread(
            target=self.check_heartbeat,
            args=(run_event, hb_int),
            daemon=True,
        )
        
        thread_fb = threading.Thread(
            target=self.dispatch_fallback,
            args=(run_event, fb_int, fb_times),
            daemon=True,
        )
        
        thread_hb.start()
        thread_fb.start()
        
        try: 
            while True:
                time.sleep(.1) # TODO: make sure this isnt an issue
        except KeyboardInterrupt:
            # TODO: won't entirely stop running until the loops finish...
            # TODO: maybe switch to asyncio ? idk i havent rly looked into it
            run_event.clear()
            thread_hb.join()
            thread_fb.join()
        
    # TODO: error handling
    def check_heartbeat(self, run_event, interval):
        while run_event.is_set():
            print(f"polling judge workers...")
            close_old_connections()

            workers = list(JudgeWorker.objects.filter(is_active=True))
            with ThreadPoolExecutor() as executor:
                for result in executor.map(poll_one_worker, workers):
                    if result is not None:
                        result.last_heartbeat = timezone.now()
                        result.save(update_fields=["last_heartbeat"])

            time.sleep(interval)
        
    def dispatch_fallback(self, run_event, interval, fb_times):
        while run_event.is_set():
            print(f"running job queue dispatch fallback...")
            close_old_connections()
            for _ in range(fb_times):
                if not dispatch_task():
                    break
            time.sleep(interval)
        

def poll_one_worker(worker):
    try:
        url = f"{worker.endpoint_url.rstrip("/")}/heartbeat"
        # TODO: potentially change timeout
        response = requests.get(url, timeout=(2, 2)) 
    except requests.RequestException:
        print(f"request to worker {worker.name} failed")
        return

    if response.status_code != 200:
        print(f"failed to get worker {worker.name} health: http {response.status_code}")
        return

    return worker

