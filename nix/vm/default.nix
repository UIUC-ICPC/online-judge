{
  inputs,
  withSystem,
  self,
  ...
}:

{
  perSystem =
    {
      system,
      pkgs,
      ...
    }:
    let
      linuxSystem = builtins.replaceStrings [ "darwin" ] [ "linux" ] system;
      vm = withSystem linuxSystem (
        { config, ... }:
        inputs.nixpkgs.lib.nixosSystem {
          system = linuxSystem;
          modules = [
            "${inputs.nixpkgs}/nixos/modules/virtualisation/qemu-vm.nix"
            { virtualisation.host.pkgs = pkgs; }
            (import ./judge-worker.nix {
              languageConfigs = config.packages.language-configs;
            })
            self.nixosModules.judge-worker
          ];
        }
      );
    in
    {
      packages = {
        judge-worker-vm = vm.config.system.build.vm;
      };
    };
}
