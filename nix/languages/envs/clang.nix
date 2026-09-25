{ buildEnv, clang }:

buildEnv {
  name = "clang-env";
  paths = [ clang ];
}
