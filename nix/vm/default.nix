{ inputs, self, ... }:

{
  perSystem =
    {
      system,
      config,
      pkgs,
      ...
    }:
    let
      patchedNixpkgs = pkgs.applyPatches {
        name = "nixpkgs-patched";
        src = inputs.nixpkgs;
        patches = [
          # HACK: Until https://nixpk.gs/pr-tracker.html?pr=563922 is merged into unstable
          (pkgs.fetchpatch2 {
            url = "https://patch-diff.githubusercontent.com/raw/NixOS/nixpkgs/pull/563922.diff";
            hash = "sha256-KU7/5hgK/XQoP8V7O4urEpr94HfbWq3RBJ3S1V0rrJA=";
          })
        ];
      };
      linuxSystem = builtins.replaceStrings [ "darwin" ] [ "linux" ] system;
      vm = import "${patchedNixpkgs}/nixos/lib/eval-config.nix" {
        system = linuxSystem;
        modules = [
          "${patchedNixpkgs}/nixos/modules/virtualisation/qemu-vm.nix"
          { virtualisation.host.pkgs = pkgs; }
          (import ./judge-worker.nix {
            languageConfigs = config.packages.language-configs;
          })
          self.nixosModules.judge-worker
        ];
      };
    in
    {
      packages = {
        judge-worker-vm = vm.config.system.build.vm;
      };
    };
}
