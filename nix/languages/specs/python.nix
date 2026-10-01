{
  perSystem = { envs, ... }: {
    languages.python = {
      environment = envs.python;
      run = {
        program = "/usr/bin/python3";
        args = [
          "{source}"
        ];
      };
    };
  };
}
