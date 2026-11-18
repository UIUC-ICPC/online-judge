{
  lib,
  judgeWorkerModule,
  languageConfigs,
}:

{
  name = "judge-worker";

  nodes.machine =
    { pkgs, ... }:
    {
      imports = [
        judgeWorkerModule
      ];

      services.judge-worker = {
        enable = true;
        configFile = languageConfigs;
      };

      # Used by the test script to submit files to the server.
      environment.systemPackages = [
        pkgs.curl
      ];

      systemd.tmpfiles.rules = [
        "L+ /test - - - - ${../../../judge-worker/tests/fixtures}"
      ];
    };

  testScript = lib.concatLines (
    map builtins.readFile [
      ./common.py
      ./cpp.py
      ./python.py
    ]
  );
}
