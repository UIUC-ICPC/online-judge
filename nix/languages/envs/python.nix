{ buildEnv, python3 }:

buildEnv {
  name = "python-env";
  paths = [ python3 ];
}
