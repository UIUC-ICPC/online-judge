from data import models

def select_worker_WLC():
    workers = models.JudgeWorker.objects.filter(is_active=True)

    if not workers.exists():
        return None

    best_worker = None
    lowest_ratio = float('inf')

    for worker in workers:
        current_ratio = worker.load_ratio()

        if (current_ratio < lowest_ratio):
            best_worker = worker
            lowest_ratio = current_ratio
            continue

    return best_worker\