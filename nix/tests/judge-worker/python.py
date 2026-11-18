with subtest("Python hello world"):
    submit_file("python", "/test/python/hello-world.py")

with subtest("service is still running"):
    machine.succeed("systemctl is-active --quiet judge-worker.service")
