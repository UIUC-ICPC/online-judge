{ craneLib, lib }:

let
  src = craneLib.cleanCargoSource ../../judge-worker;
  commonArgs = {
    inherit src;
    strictDeps = true;
  };
  cargoArtifacts = craneLib.buildDepsOnly commonArgs;
in
craneLib.buildPackage (
  commonArgs
  // {
    inherit cargoArtifacts;
    meta = {
      description = "Judge worker for UIUC IPL";
      mainProgram = "judge-worker";
      platforms = lib.platforms.linux;
    };
  }
)
