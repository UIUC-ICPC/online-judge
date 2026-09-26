{
  imports = [
    ./envs
    ./specs
  ];
  perSystem =
    { config, pkgs, ... }:
    let
      language-configs = pkgs.writeText "language-configs.json" (builtins.toJSON config.languages);
    in
    {
      packages = {
        inherit language-configs;
      };
    };
}
