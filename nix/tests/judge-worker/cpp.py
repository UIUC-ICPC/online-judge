# NOTE: the server currently accepts a submission and exercises the isolate box
# lifecycle, but does not judge the source code yet. these cases check that each
# fixture can be submitted over HTTP. once the handler returns a verdict, we can
# assert it here

with subtest("hello world"):
    submit_file("cpp20-gcc", "/test/cpp/hello-world.cpp")

with subtest("compile error"):
    submit_file("cpp20-gcc", "/test/cpp/compile-error.cpp")

with subtest("infinite compile time"):
    submit_file("cpp20-gcc", "/test/cpp/infinite-compile-time.cpp")

with subtest("runtime error"):
    submit_file("cpp20-gcc", "/test/cpp/runtime-error.cpp")

with subtest("non-zero exit"):
    submit_file("cpp20-gcc", "/test/cpp/non-zero-exit.cpp")

with subtest("infinite loop"):
    submit_file("cpp20-gcc", "/test/cpp/infinite-loop.cpp")

with subtest("memory limit"):
    submit_file("cpp20-gcc", "/test/cpp/memory-limit.cpp")

with subtest("filesystem write"):
    submit_file("cpp20-gcc", "/test/cpp/fs-write.cpp")

with subtest("stderr"):
    submit_file("cpp20-gcc", "/test/cpp/stderr.cpp")

with subtest("fork"):
    submit_file("cpp20-gcc", "/test/cpp/fork.cpp")

with subtest("fork bomb"):
    submit_file("cpp20-gcc", "/test/cpp/forkbomb.cpp")
