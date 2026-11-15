# Backend Development

## Build & Setup 

The project uses `uv` to install and manage Python dependencies.

Install/sync dependencies 
```
uv sync
```

Generate a random secret key
```
uv run python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Ensure your `.env` file is properly set up with the following information:
```
DJANGO_ENV=development
DJANGO_SECRET_KEY=put-generated-key-here
MYSQL_DATABASE=online_judge
MYSQL_USER=someuser
MYSQL_PASSWORD="somepassword"
MYSQL_HOST=put.hostname.here
MYSQL_PORT=somenumber
```

Run: 
```
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Django should start up a server at `http://127.0.0.1:8000/`

## Submission acceptance

Contest source uploads use `web.forms.SubmissionForm`. Configure the accepted
worker language IDs with `SUBMISSION_LANGUAGES` in `app/settings.py`. The same
choices populate the upload form. The defaults allow `cpp17-gcc`, one nonempty
UTF-8 source file up to 256 KiB, and one submission per team per second. The
limits are controlled by `SUBMISSION_MAX_SOURCE_BYTES` and
`SUBMISSION_COOLDOWN_SECONDS`; setting the cooldown to zero disables it.
Configure a total request-body limit at the HTTP proxy as well: Django's
upload memory threshold is not a file-size rejection limit.

`web.services.create_submission()` rechecks contest access and team membership,
then atomically saves the source text, a `Pending` submission, and a judging
attempt. Invalid inputs return the problem page with field errors (HTTP 400),
and the cooldown returns HTTP 429 with `Retry-After`. Successful uploads redirect
to an owner-only submission detail page, which stays accessible after the
contest ends.

HTTP dispatch and SSE are not implemented by this acceptance path. When merging
the worker-server branch, enqueue the judging ID using `transaction.on_commit()`
after the records have been saved. Network calls must not run inside the
submission transaction. Keep dispatch retryable so a worker/network outage does
not lose the saved submission.
