{
  imports = [
    ./envs
    ./specs
  ];
  perSystem =
    { config, pkgs, ... }:
    let
      languageConfigs = pkgs.writeText "language-configs.json" (builtins.toJSON config.languages);
    in
    {
      packages = {
        language-configs = languageConfigs;
      };
    };
}
