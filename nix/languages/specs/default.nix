{
  imports = [
    ./cpp.nix
    ./python.nix
  ];
  perSystem =
    { lib, ... }:
    let
      command = lib.types.submodule {
        options = {
          program = lib.mkOption {
            type = lib.types.str;
          };
          args = lib.mkOption {
            type = lib.types.listOf lib.types.str;
            default = [ ];
          };
        };
      };
    in
    {
      options.languages = lib.mkOption {
        type = lib.types.attrsOf (
          lib.types.submodule {
            options = {
              environment = lib.mkOption {
                type = lib.types.package;
              };
              compile = lib.mkOption {
                type = lib.types.listOf command;
                default = [ ];
              };
              run = lib.mkOption {
                type = command;
              };
            };
          }
        );
        default = { };
      };
    };
}
