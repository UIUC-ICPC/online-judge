# Judge Worker Development

The judge worker executes submissions inside [`isolate`](https://www.ucw.cz/moe/isolate.1.html) sandboxes.

Because `isolate` depends on Linux-specific functionality such as cgroups and namespaces, the full worker environment is tested using NixOS.

## Setup

### macOS Linux builder

1. Install [nix-darwin](https://github.com/nix-darwin/nix-darwin) using flakes.
2. Install or update Rosetta:

   ```sh
   softwareupdate --install-rosetta --agree-to-license
   ```

3. Add the following to your nix-darwin configuration:

   ```nix
   nix.linux-builder = {
     enable = true;
     package = pkgs.darwin.linux-builder-vz;
     systems = [ "aarch64-linux" ];
     supportedFeatures = [
       "kvm"
       "benchmark"
       "big-parallel"
       "nixos-test"
     ];
     config.virtualisation.vz = {
       rosetta.enable = false;
       nestedVirtualization = true;
     };
   };
   ```

4. Rebuild your nix-darwin configuration:

   ```sh
   sudo darwin-rebuild switch
   ```

### KVM permissions

The development VM uses KVM acceleration when available.

If the VM reports `/dev/kvm: Permission denied`, check the permissions with:

```sh
ls -l /dev/kvm
```

If `/dev/kvm` is only accessible to the `kvm` group, add your user to it:

```sh
sudo usermod -aG kvm "$USER"
```

Then log out and back in. On WSL, restart WSL from Windows with:

```powershell
wsl --shutdown
```

After restarting, verify that your user has access:

```sh
test -r /dev/kvm && test -w /dev/kvm && echo "KVM accessible"
```

## NixOS integration test

The judge worker has a NixOS integration test that boots a VM and tests the worker in its real sandbox environment.

Run it with:

```sh
nix build -L .#checks.x86_64-linux.judge-worker
```

The test uses fixtures from:

```text
judge-worker/tests/fixtures/
```

Use the integration test for behavior that depends on `isolate`, cgroups, resource limits, or NixOS configuration.

## Development VM

An interactive NixOS VM is available for manually debugging the judge worker and sandbox environment.

Launch the VM with from the project root:

```sh
SHARED_DIR="$PWD" nix run .#judge-worker-vm
```

The VM contains the judge worker, language configuration, and test fixtures.

The virtual machine shares the project directory with the host machine, so changes from one will appear in the other.
The project is mounted at `/tmp/shared`, and the VM starts in `/tmp/shared/judge-worker` for judge-worker development.

### Development workflow

The intended workflow is:

1. Edit the source code on the host machine.
2. Build the judge worker inside the VM.
3. Run a test submission inside the VM.

After editing the project on the host, build the worker in the VM with:

```sh
cargo build
```

Then run a submission with:

```sh
judge-run -l cpp20-gcc -s ./tests/fixtures/cpp/hello-world.cpp
```

`judge-run` runs the locally built debug binary as the `judge-worker` system user and group with the VM's language configuration.

Language configuration can be found at:

```text
/etc/judge-worker/language-configs.json
```

The development VM is intended for interactive debugging.
Automated judge-worker behavior should generally be covered by the NixOS integration test.
