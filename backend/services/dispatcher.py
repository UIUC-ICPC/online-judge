from data import models
import base64
import requests
from django.db import transaction
from data.models import JudgeWorker, Judging
from datetime import timedelta
from django.utils import timezone
# from django.db import close_old_connections TODO: where do i need this


FAILURE_THRESHOLD = 20 

class WorkerNotAvailable(Exception):
    pass

class InvalidSubmission(Exception):
    pass


# TODO: authenticate the control server 
# TODO: deal with error handling - when should it be requeued
# TODO: ensure properly nonblocking methods
def dispatch_task():
    print("checking for available task...")
    judging = reserve_task()
    if judging is None:
        print("no task found")
        return False

    print("attempting to dispatch job...")
    try:
        _send_to_worker(judging)
        judging.set_if_dispatching(Judging.Status.RUNNING)
        return True
    except InvalidSubmission:
        judging.set_if_dispatching(Judging.Status.FAILED)
        return True
    except Exception: # tries to requeue - TODO: is this too generic?
        judging.set_if_dispatching(Judging.Status.QUEUED)
    return False

    
@transaction.atomic
def reserve_task():
    workers = list(
        _get_healthy_workers()
        .select_for_update(skip_locked=True)
    )
    if not workers:
        return None
    
    worker = _select_worker_WLC(workers)
    if worker is None:
        return None
    
    judging = (
        Judging.objects.select_for_update(skip_locked=True)
        .filter(status=Judging.Status.QUEUED)
        .order_by("created_at")
        .first()
    )
    
    if judging is None:
        return
    
    judging.worker = worker
    judging.status = Judging.Status.DISPATCHING
    judging.save(update_fields=["worker", "status"])
    return judging


def _send_to_worker(judging):
    url = f"{judging.worker.endpoint_url.rstrip('/')}/submissions"
    entry = judging.submission
    
    body = {
        "language": entry.language,
        "source": base64.b64encode(entry.source_code).decode("utf-8"),
        "problem_name": f"{entry.problem.blob_name}.zip"
    }
    
    response = requests.post(url, json=body, timeout=(2,2))
    # TODO: may not need these custom exceptions 
    if response.status_code == 503: 
        raise WorkerNotAvailable(response.text)
    if response.status_code != 202:
        raise InvalidSubmission(response.text)
    return response.json()
    
    
def _select_worker_WLC(workers):
    return workers[0]
    # TODO: load balancer algo (commented out for testing)
    # best_worker = None
    # lowest_ratio = float('inf')

    # for worker in workers:
    #     current_ratio = worker.load_ratio

    #     if (current_ratio < lowest_ratio):
    #         best_worker = worker
    #         lowest_ratio = current_ratio
    #         continue

    # return best_worker
    
    
def _get_healthy_workers():
    cutoff = timezone.now() - timedelta(seconds=FAILURE_THRESHOLD)

    return JudgeWorker.objects.filter(
        is_active=True,
        last_heartbeat__gte=cutoff
    )
    
