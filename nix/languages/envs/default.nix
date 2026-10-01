{
  perSystem =
    { lib, pkgs, ... }:
    let
      envs = {
        clang = pkgs.callPackage ./clang.nix { };
        gcc = pkgs.callPackage ./gcc.nix { };
        python = pkgs.callPackage ./python.nix { };
      };
      envPackages = lib.mapAttrs' (name: env: lib.nameValuePair "${name}-env" env) envs;
    in
    {
      _module.args.envs = envs;
      packages = envPackages;
    };
}
