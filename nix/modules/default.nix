{ withSystem, ... }:
{
  flake.nixosModules.judge-worker =
    { pkgs, config, ... }:
    {
      imports = [
        ./judge-worker
      ];

      services.judge-worker = {
        package = withSystem pkgs.stdenv.hostPlatform.system (
          { config, ... }:
          config.packages.judge-worker
        );
        configFile = withSystem pkgs.stdenv.hostPlatform.system (
          { config, ... }:
          config.packages.language-configs
        );
      };

      environment.systemPackages = [
        config.services.judge-worker.package
      ];
    };
}
