start_all()


def submission_command(language, source):
    return (
        "sudo -u judge-worker -g judge-worker "
        "judge-worker "
        "-c /etc/judge-worker/language-configs.json "
        f"-l {language} "
        f"-s {source}"
    )


def run_submission(language, source):
    return machine.succeed(submission_command(language, source))


def fail_submission(language, source):
    return machine.fail(submission_command(language, source))


with subtest("isolate environment"):
    machine.succeed("sudo -u judge-worker -g judge-worker isolate --init")
    machine.succeed("sudo -u judge-worker -g judge-worker isolate --cleanup")
