{ inputs, ... }:
{
  perSystem =
    {
      config,
      lib,
      pkgs,
      ...
    }:
    {
      checks.judge-worker = pkgs.testers.runNixOSTest (
        import ./judge-worker {
          inherit lib;
          judgeWorkerModule = inputs.self.nixosModules.judge-worker;
          languageConfigs = config.packages.language-configs;
        }
      );
    };
}
