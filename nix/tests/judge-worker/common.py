import json
import shlex

start_all()

machine.wait_for_unit("judge-worker.service")
machine.wait_for_open_port(3000)

BASE_URL = "http://127.0.0.1:3000"


def http_request(method, path="/", data=None, content_type="application/json"):
    arguments = [
        "curl",
        "--silent",
        "--show-error",
        "--max-time",
        "60",
        "--output",
        "/tmp/judge-worker-response",
        "--write-out",
        "'%{http_code}'",
        "--request",
        method,
    ]

    if data is not None:
        arguments += [
            "--header",
            shlex.quote(f"Content-Type: {content_type}"),
            "--data",
            shlex.quote(data),
        ]

    arguments.append(f"{BASE_URL}{path}")

    status = int(machine.succeed(" ".join(arguments)).strip())
    body = machine.succeed("cat /tmp/judge-worker-response")
    return status, body


def submit(language, source):
    return http_request(
        "POST", data=json.dumps({"language": language, "source": source})
    )


def submit_file(language, source_path):
    source = machine.succeed(f"cat {source_path}")
    status, body = submit(language, source)
    t.assertEqual(
        status,
        200,
        f"submission of {source_path} failed with HTTP {status}: {body}",
    )
    return body


with subtest("isolate environment"):
    machine.succeed("sudo -u judge-worker -g judge-worker isolate --init")
    machine.succeed("sudo -u judge-worker -g judge-worker isolate --cleanup")

with subtest("unknown language"):
    status, _ = submit("not-a-language", "int main() {}")
    t.assertEqual(status, 400)

with subtest("malformed request"):
    status, _ = http_request("POST", data="not json")
    t.assertIn(status, (400, 415, 422))

with subtest("missing fields"):
    status, _ = http_request("POST", data=json.dumps({"language": "cpp20-gcc"}))
    t.assertEqual(status, 422)

with subtest("unsupported method"):
    status, _ = http_request("GET")
    t.assertEqual(status, 405)
