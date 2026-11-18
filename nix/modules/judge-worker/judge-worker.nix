{ config, lib, ... }:

let
  inherit (lib)
    mkEnableOption
    mkIf
    mkOption
    types
    ;

  cfg = config.services.judge-worker;
in
{
  options.services.judge-worker = {
    enable = mkEnableOption "the judge-worker HTTP server";

    package = mkOption {
      type = types.package;
      description = ''
        The judge-worker package to run.
      '';
    };

    configFile = mkOption {
      type = types.path;
      description = ''
        Path to the language configuration JSON file.
      '';
    };
  };

  config = lib.mkMerge [
    (mkIf cfg.enable {
      systemd.services.judge-worker = {
        description = "Judge worker HTTP server";
        wantedBy = [ "multi-user.target" ];
        after = [ "isolate.service" ];
        requires = [ "isolate.service" ];

        # The setuid isolate wrapper lives in /run/wrappers/bin, which is not on
        # the default PATH for system services.
        path = [ "/run/wrappers" ];

        serviceConfig = {
          ExecStart = "${lib.getExe cfg.package} --config ${cfg.configFile}";
          User = "judge-worker";
          Group = "judge-worker";
          Restart = "on-failure";
          RestartSec = 2;
        };
      };
    })

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
  ];
}
