{ config, lib, ... }:

{
  security = {
    isolate.enable = true;
    wrappers.isolate = {
      source = lib.getExe config.security.isolate.finalPackage;
      owner = "root";
      group = "judge-worker";
      setuid = true;
      permissions = "u+rx,g+x";
    };
  };

  users = {
    groups.judge-worker = { };
    users.judge-worker = {
      isSystemUser = true;
      group = "judge-worker";
    };
  };
}
