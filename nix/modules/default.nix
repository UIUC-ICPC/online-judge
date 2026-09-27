{ withSystem, ... }:
{
  flake.nixosModules.judge-worker = { pkgs, ... }: {
    imports = [
      ./judge-worker
    ];
    # TODO: Change to a option definition once judge-worker becomes a service
    environment.systemPackages = [
      (withSystem pkgs.stdenv.hostPlatform.system (
        { config, ... }:
        config.packages.judge-worker
      ))
    ];
  };
}
