from django.db import models
from django.conf import settings
from django.utils import timezone


class JudgeWorker(models.Model):
    name = models.CharField(max_length=255, unique=True)
    endpoint_url = models.CharField(max_length=255)
    weight = models.PositiveIntegerField(default=1)  # Hardware weight capacity for WLC
    active_connections = models.PositiveIntegerField(
        default=0
    )  # Active submissions being evaluated
    is_active = models.BooleanField(default=True)
    last_heartbeat = models.DateTimeField(default=timezone.now)

    @property
    def load_ratio(self):
        """Calculates dynamic load ratio C_i / W_i"""
        if self.weight == 0:
            return float("inf")
        return self.active_connections / self.weight

    def __str__(self):
        return f"{self.name} (Active: {self.active_connections}, Weight: {self.weight})"


class Contest(models.Model):
    title = models.CharField(max_length=255)
    private = models.BooleanField(default=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="contest_end_after_start",
            )
        ]


class Problem(models.Model):
    class StatementType(models.TextChoices):
        UNKNOWN = "unknown", "Unknown"
        HTML = "html", "HTML"
        PDF = "pdf", "PDF"
        TEXT = "text", "Plain text"

    blob_name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)
    statement_type = models.CharField(
        max_length=255, choices=StatementType.choices, default=StatementType.UNKNOWN
    )


class ContestProblem(models.Model):
    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.PROTECT,
    )
    label = models.CharField(max_length=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["contest", "problem"],
                name="unique_contest_problem",
            ),
            models.UniqueConstraint(
                fields=["contest", "label"],
                name="unique_contest_label",
            ),
        ]


# FIXME: right now, "empty" contest teams will continue to exist
class ContestTeam(models.Model):
    name = models.CharField(max_length=255)
    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name="teams",
    )


class ContestWriters(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contest_writers",
    )
    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name="writers",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "contest"], name="unique_contest_writer"
            )
        ]

    def __str__(self):
        return self.user.username


# FIXME: ensure user may only join one team per contest
class ContestParticipant(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contest_participations",
    )
    team = models.ForeignKey(
        ContestTeam,
        on_delete=models.CASCADE,
        related_name="participants",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "team"],
                name="unique_user_team_participation",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.team.name}"


# TODO: verdict and status should be textchoices
class Submission(models.Model):
    team = models.ForeignKey(
        ContestTeam,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submissions",
    )
    contest = models.ForeignKey(
        Contest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submissions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="submissions",
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.PROTECT,
        related_name="submissions",
    )
    language = models.CharField(max_length=255)
    submitted_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=255)
    verdict = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    source_code = models.BinaryField()

    class Meta:
        indexes = [
            models.Index(
                fields=["contest", "problem", "submitted_at"],
                name="submission_contest_problem_idx",
            ),
            models.Index(
                fields=["team", "contest"],
                name="submission_team_contest_idx",
            ),
        ]

    def __str__(self):
        return f"Submission #{self.pk}"


class Judging(models.Model):
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="judgings",
    )
    verdict = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    # worker = models.ForeignKey(
    #     JudgeWorker,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="judgings",
    # )

    def __str__(self):
        return f"Judging #{self.pk} for submission #{self.submission_id}"


class TestRun(models.Model):
    test_case_id = models.IntegerField()
    judging = models.ForeignKey(
        Judging,
        on_delete=models.CASCADE,
        related_name="test_runs",
    )
    runtime_ms = models.PositiveIntegerField(null=True, blank=True)
    memory_kb = models.PositiveIntegerField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=255)
    verdict = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["judging", "test_case_id"],
                name="unique_judging_test_case",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(finished_at__isnull=True)
                    | (
                        models.Q(started_at__isnull=False)
                        & models.Q(finished_at__gte=models.F("started_at"))
                    )
                ),
                name="valid_test_run_time",
            ),
        ]

    def __str__(self):
        return f"Test run #{self.pk}"
