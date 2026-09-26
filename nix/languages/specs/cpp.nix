{
  perSystem =
    { lib, envs, ... }:
    let
      common-args = [
        "-O2"
      ];

      versions = [
        "17"
        "20"
        "23"
      ];

      mk-gcc =
        version:
        lib.nameValuePair "cpp${version}-gcc" {
          environment = envs.gcc;
          compile = [
            {
              program = "/usr/bin/g++";
              args = common-args ++ [
                "-std=c++${version}"
                "{source}"
                "-o"
                "{output}"
              ];
            }
          ];
          run.program = "{output}";
        };

      mk-clang =
        version:
        lib.nameValuePair "cpp${version}-clang" {
          environment = envs.clang;
          compile = [
            {
              program = "/usr/bin/clang++";
              args = common-args ++ [
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
      languages = lib.listToAttrs ((map mk-gcc versions) ++ (map mk-clang versions));
    };
}
