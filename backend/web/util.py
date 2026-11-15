from django.utils import timezone
from data.models import ContestParticipant
from django.core.exceptions import PermissionDenied


def validate_contest_access(user, contest):
    now = timezone.now()

    if contest.start_time > now:
        raise PermissionDenied("Contest has not started.")
    if contest.end_time <= now:
        raise PermissionDenied("Contest has ended.")
    if not ContestParticipant.objects.filter(user=user, team__contest=contest).exists():
        raise PermissionDenied("You do not have permission to view this contest.")
