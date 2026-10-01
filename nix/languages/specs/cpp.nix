{
  perSystem =
    { lib, envs, ... }:
    let
      commonArgs = [
        "-O2"
      ];

      versions = [
        "17"
        "20"
        "23"
      ];

      mkGcc =
        version:
        lib.nameValuePair "cpp${version}-gcc" {
          environment = envs.gcc;
          compile = [
            {
              program = "/usr/bin/g++";
              args = commonArgs ++ [
                "-std=c++${version}"
                "{source}"
                "-o"
                "{output}"
              ];
            }
          ];
          run.program = "{output}";
        };

      mkClang =
        version:
        lib.nameValuePair "cpp${version}-clang" {
          environment = envs.clang;
          compile = [
            {
              program = "/usr/bin/clang++";
              args = commonArgs ++ [
                "-std=c++${version}"
                "{source}"
                "-o"
                "{output}"
              ];
            }
          ];
          run.program = "{output}";
        };
    in
    {
      languages = lib.listToAttrs ((map mkGcc versions) ++ (map mkClang versions));
    };
}
