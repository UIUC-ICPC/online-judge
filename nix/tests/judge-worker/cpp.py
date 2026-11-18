with subtest("hello world"):
    output = run_submission("cpp20-gcc", "/test/cpp/hello-world.cpp")
    t.assertIn("Hello, world!", output)

with subtest("compile error"):
    run_submission("cpp20-gcc", "/test/cpp/compile-error.cpp")

with subtest("infinite compile time"):
    run_submission("cpp20-gcc", "/test/cpp/infinite-compile-time.cpp")

with subtest("runtime error"):
    run_submission("cpp20-gcc", "/test/cpp/runtime-error.cpp")

with subtest("non-zero exit"):
    run_submission("cpp20-gcc", "/test/cpp/non-zero-exit.cpp")

with subtest("infinite loop"):
    run_submission("cpp20-gcc", "/test/cpp/infinite-loop.cpp")

with subtest("memory limit"):
    run_submission("cpp20-gcc", "/test/cpp/memory-limit.cpp")

with subtest("filesystem write"):
    run_submission("cpp20-gcc", "/test/cpp/fs-write.cpp")

with subtest("stderr"):
    output = machine.succeed(
        submission_command("cpp20-gcc", "/test/cpp/stderr.cpp") + " 2>&1"
    )
    t.assertIn("stderr", output)

with subtest("fork"):
    run_submission("cpp20-gcc", "/test/cpp/fork.cpp")

with subtest("fork bomb"):
    run_submission("cpp20-gcc", "/test/cpp/forkbomb.cpp")
