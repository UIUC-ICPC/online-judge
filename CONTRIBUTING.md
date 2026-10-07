# Contributing 

For this repository we will be following a [trunk based development](https://trunkbaseddevelopment.com/) branching model, so please make a new branch for any new features. Branches will be closed on successful merge to main.

For discussion off of github, please join our community [here](https://discord.gg/eWcbBd7Vcf). We also have a private discord server for more specific infra discussion, if you're not in it and would like to be, please DM a maintainer.

## Issues 
- For new features that haven't been previously discussed, start an issue to discuss planned changes.
- Please put any bugs/issues into issues with the proper labels.
- Make sure your issue is descriptive, include screenshots if necessary.
- For bugs, please include steps on how to recreate the bug.

## Contribution Workflow

Do not push directly to the `main` branch. All changes must go through a code review. Please follow these steps:

1. Create a Branch: Fork the repository (if you are an external contributor) or create a new branch within the organization.
2. Sync with Main: Before writing any code, ensure your branch is up to date by running `git pull origin main`.
3. Commit & Push: Make your changes, then `git add`, `git commit`, and `git push` to your branch. 
   * Note on Commits: Make your commit messages descriptive of the changes made. A vague message like `add changes` is not sufficient.
4. Open a Pull Request: Create a PR to merge your branch into `main`. Briefly summarize the exact changes you made inside the PR description.
5. Approval: All PRs must be reviewed and approved by a maintainer before they can be merged.

## Development environment

This repository uses [Nix](https://nixos.org) to provide the development environment and project dependencies.
For easy installation we recommend the [Determinate Nix Installer](https://github.com/DeterminateSystems/nix-installer). 
The [offical](https://nix.dev/install-nix) nix installer also works, but [flakes](https://nix.dev/concepts/flakes.html) will need to be [manually enabled](https://wiki.nixos.org/wiki/Flakes#Nix_standalone).

Enter the development shell with:

```sh
nix develop
```

Most development tools, including Rust tooling, are available from this shell.

### direnv

For automatic development shell activation, we recommend using
[direnv](https://direnv.net/) together with
[nix-direnv](https://github.com/nix-community/nix-direnv).

After installing both, enable the repository's environment with:

```sh
direnv allow
```

direnv reads from `.envrc`, which uses the project's Nix flake, so the development environment will be loaded automatically whenever you enter the repository.

Using direnv is optional, `nix develop` provides the same development environment manually.

## Checks

Run the repository checks with:

```sh
nix flake check
```

These checks are the same that are ran by CI, so if this passes locally it will pass on CI.

## Project-specific development

Some components have additional development and testing requirements.

- [Judge worker](docs/judge-worker.md)
