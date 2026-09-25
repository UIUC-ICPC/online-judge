{
  perSystem =
    {
      config,
      lib,
      pkgs,
      ...
    }:
    {
      devShells.default = pkgs.mkShell {
        shellHook = ''
          ${config.pre-commit.shellHook}
        '';
        packages =
          with pkgs;
          [
            # General
            git

            # Rust
            cargo
            clippy
            rust-analyzer
            rustc
          ]
          ++ config.pre-commit.settings.enabledPackages
          ++ lib.optionals pkgs.stdenv.hostPlatform.isLinux [
            isolate
          ];
      };
    };
}
