import hashlib
from functools import wraps
from django.utils import timezone
from data.models import JudgeWorker
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.db import transaction
from services.dispatcher import dispatch_task


def worker_required(view):
    @wraps(view)
    def fn(request, *args, **kwargs):
        worker = _authenticate_worker(request)

        if worker is None:
            return HttpResponse(
                headers={"WWW-Authenticate": "Bearer"},
                status=401
            )
        request.worker = worker
        return view(request, *args, **kwargs)
        
    return fn


def _authenticate_worker(request):
    token = request.headers.get("Authorization", "").split()
    
    if len(token) != 2 or token[0].lower() != "bearer":
        return None
    
    hash = hashlib.sha256(token[1].encode()).hexdigest()
    exists = JudgeWorker.objects.filter(auth_key_hash=hash).first()
    return exists


@csrf_exempt
@require_POST
@worker_required
@transaction.atomic
def finished_judging_task(request):   
   # TODO: update information about related judging and send sse to client
   print("finished juding task ! ! ! !")
   transaction.on_commit(dispatch_task)
   return
