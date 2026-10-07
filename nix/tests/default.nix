{ self, withSystem, ... }:
{
  perSystem =
    { config, system, ... }:
    let
      linuxSystem = builtins.replaceStrings [ "darwin" ] [ "linux" ] system;
    in
    {
      checks.judge-worker = withSystem linuxSystem (
        { pkgs, config, ... }:
        pkgs.testers.runNixOSTest (
          import ./judge-worker {
            inherit (pkgs) lib;
            judgeWorkerModule = self.nixosModules.judge-worker;
            languageConfigs = config.packages.language-configs;
          }
        )
      );
      packages.judge-worker-test = config.checks.judge-worker;
    };
}
