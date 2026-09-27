{
  # HACK: Until https://nixpk.gs/pr-tracker.html?pr=567288 lands in unstable
  disabledModules = [
    "security/isolate.nix"
  ];
  imports = [
    ./isolate.nix
    ./judge-worker.nix
  ];
}
