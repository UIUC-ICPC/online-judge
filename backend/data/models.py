from django.db import models
from django.conf import settings
from django.utils import timezone

# TODO sync these changes w any new changes 
class Contest(models.Model):
	private = models.BooleanField(default=False)
	password = models.CharField(
		max_length=255,blank=True,
	) 
	title = models.CharField(max_length=255)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
    
    
class Problem(models.Model):
	memory_limit = models.IntegerField()
	time_limit = models.IntegerField()
	output_limit = models.IntegerField()
	name = models.CharField(max_length=255)

 
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


class ContestTeam(models.Model):
    name = models.CharField(max_length=255)
    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name="teams",
    )


class ContestParticipant(models.Model):
    class Role(models.TextChoices):
        AUTHOR = "author", "Author"
        COMPETITOR = "competitor", "Competitor"

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
    role = models.CharField(
        max_length=255,
        choices=Role.choices,
    )


    class Meta:
        db_table = "contest_participants"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "team"],
                name="unique_user_team_participation",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.team.name} ({self.role})"

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
    source_code = models.TextField()

    class Meta:
        db_table = "submissions"
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


    class Meta:
        db_table = "judgings"


    def __str__(self):
        return f"Judging #{self.pk} for submission #{self.submission_id}"


class TestRun(models.Model):
    test_case_id = models.IntegerField()
    judging = models.ForeignKey(
        Judging,
        on_delete=models.CASCADE,
        related_name="test_runs",
    )
    runtime_ms = models.IntegerField(null=True, blank=True)
    memory_kb = models.IntegerField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=255)
    verdict = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )


    class Meta:
        db_table = "test_runs"
        indexes = [
            models.Index(
                fields=["judging", "test_case_id"],
                name="testrun_judging_case_idx",
            ),
        ]


    def __str__(self):
        return f"Test run #{self.pk}"


    
    

