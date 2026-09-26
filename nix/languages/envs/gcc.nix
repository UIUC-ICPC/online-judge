{ buildEnv, gcc }:

buildEnv {
  name = "gcc-env";
  paths = [ gcc ];
}
