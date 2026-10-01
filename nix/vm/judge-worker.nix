{ languageConfigs }:
{ pkgs, ... }:

let
  cargoTargetDir = "/var/cache/judge-worker/target";
in
{
  environment.interactiveShellInit = ''
    cat <<'EOF'

    --- Judge Worker Dev VM ---

    To share the project directory, start this VM with:
      SHARED_DIR="$PWD" nix run .#judge-worker-vm

    The project will be available at:
      /tmp/shared

    Useful commands:
      cargo build
      judge-run -l <language> -s <source-file>

    Language config:
      /etc/judge-worker/language-configs.json

    Fish is also supported, to use run:
      fish

    EOF
  '';

  networking.hostName = "judge-worker-dev";

  systemd.tmpfiles.rules = [
    "d /var/cache/judge-worker 0755 root root -"
  ];

  environment = {
    loginShellInit = ''
      if [ -d /tmp/shared/judge-worker ]; then
        cd /tmp/shared/judge-worker
      fi
    '';
    etc."judge-worker/language-configs.json".source = languageConfigs;
    shellAliases.judge-run = "sudo -u judge-worker -g judge-worker ${cargoTargetDir}/debug/judge-worker -c /etc/judge-worker/language-configs.json";
    # Keep Linux VM build artifacts separate from the host's target/.
    variables.CARGO_TARGET_DIR = cargoTargetDir;
  };

  virtualisation = {
    memorySize = 4096;
    cores = 4;
    sharedDirectories.shared.cache = "never";
  };

  programs.fish.enable = true;
  environment.systemPackages = with pkgs; [
    cargo
    rustc
    stdenv.cc
  ];

  users.users.root.password = "root";
  services.getty.autologinUser = "root";
  system.stateVersion = "26.05";
}
