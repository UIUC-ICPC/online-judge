{ inputs, ... }:

{
  perSystem =
    { pkgs, ... }:
    let
      craneLib = inputs.crane.mkLib pkgs;
    in
    {
      packages.judge-worker = pkgs.callPackage ./judge-worker.nix {
        inherit craneLib;
      };
    };
}
