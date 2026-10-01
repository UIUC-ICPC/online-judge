{
  lib,
  judgeWorkerModule,
  languageConfigs,
}:

{
  name = "judge-worker";

  nodes.machine = {
    imports = [
      judgeWorkerModule
    ];

    environment.etc = {
      "judge-worker/language-configs.json".source = languageConfigs;
    };

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
