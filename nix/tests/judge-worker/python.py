with subtest("Python hello world"):
    output = run_submission("python", "/test/python/hello-world.py")
    t.assertIn("Hello, world!", output)
