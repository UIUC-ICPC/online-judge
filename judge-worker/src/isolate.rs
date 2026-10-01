use crate::language_config::{Command, LanguageConfig};
use std::{
    fs,
    path::{Path, PathBuf},
    process::{Command as ProcessCommand, ExitStatus},
    time::Duration,
};

pub struct IsolateBox {
    box_id: u32,
    box_dir: PathBuf,
}

// https://www.ucw.cz/isolate/isolate.1.html#_limits
#[derive(Debug, Clone, Default)]
pub struct Limits {
    pub memory_kib: Option<u64>,
    pub time: Option<Duration>,
    pub wall_time: Option<Duration>,
    pub extra_time: Option<Duration>,
    pub stack_kib: Option<u64>,
    pub open_files: Option<u32>,
    pub file_size_kib: Option<u64>,
    pub core_size_kib: Option<u64>,
    pub processes: ProcessLimit,
}

#[derive(Debug, Clone, Copy, Default)]
pub enum ProcessLimit {
    #[default]
    Default,
    Max(u32),
    Unlimited,
}

#[derive(Debug, Clone, Copy)]
pub struct DiskQuota {
    pub blocks: u64,
    pub inodes: u64,
}

impl IsolateBox {
    pub fn new(box_id: u32, quota: Option<DiskQuota>) -> Result<Self, Box<dyn std::error::Error>> {
        let mut isolate = ProcessCommand::new("isolate");
        isolate.arg(format!("--box-id={box_id}")).arg("--cg");
        if let Some(quota) = quota {
            isolate.arg(format!("--quota={},{}", quota.blocks, quota.inodes));
        }
        let output = isolate.arg("--init").output()?;

        if !output.status.success() {
            return Err(format!(
                "failed to initialize isolate box: {}",
                String::from_utf8_lossy(&output.stderr)
            )
            .into());
        }

        let root = String::from_utf8(output.stdout)?;
        let box_dir = PathBuf::from(root.trim()).join("box");

        Ok(Self { box_id, box_dir })
    }

    fn isolate(&self) -> ProcessCommand {
        let mut command = ProcessCommand::new("isolate");
        command.arg(format!("--box-id={}", self.box_id));
        command
    }

    fn expand_arg(arg: &str, substitutions: &[(&str, &str)]) -> String {
        substitutions
            .iter()
            .fold(arg.to_owned(), |expanded, (key, value)| {
                expanded.replace(key, value)
            })
    }

    fn apply_limits(command: &mut ProcessCommand, limits: &Limits) {
        if let Some(memory_kib) = limits.memory_kib {
            command.arg(format!("--cg-mem={memory_kib}"));
        }
        if let Some(time) = limits.time {
            command.arg(format!("--time={}", time.as_secs_f64()));
        }
        if let Some(wall_time) = limits.wall_time {
            command.arg(format!("--wall-time={}", wall_time.as_secs_f64()));
        }
        if let Some(extra_time) = limits.extra_time {
            command.arg(format!("--extra-time={}", extra_time.as_secs_f64()));
        }
        if let Some(stack_kib) = limits.stack_kib {
            command.arg(format!("--stack={stack_kib}"));
        }
        if let Some(open_files) = limits.open_files {
            command.arg(format!("--open-files={open_files}"));
        }
        if let Some(file_size_kib) = limits.file_size_kib {
            command.arg(format!("--fsize={file_size_kib}"));
        }
        if let Some(core_size_kib) = limits.core_size_kib {
            command.arg(format!("--core={core_size_kib}"));
        }
        match limits.processes {
            ProcessLimit::Default => {}
            ProcessLimit::Max(max) => {
                command.arg(format!("--processes={max}"));
            }
            ProcessLimit::Unlimited => {
                command.arg("--processes");
            }
        }
    }

    fn run(
        &self,
        command: &Command,
        language: &LanguageConfig,
        source: &str,
        output: &str,
        writable: bool,
        limits: &Limits,
    ) -> Result<ExitStatus, Box<dyn std::error::Error>> {
        let substitutions = [("{source}", source), ("{output}", output)];
        let box_mount = if writable {
            format!("--dir=/box={}:rw", self.box_dir.display())
        } else {
            format!("--dir=/box={}", self.box_dir.display())
        };

        let usr_mount = format!("--dir=/usr={}", language.environment.display());

        let program = Self::expand_arg(&command.program, &substitutions);

        let mut isolate = self.isolate();

        isolate
            .arg("--no-default-dirs")
            .arg(box_mount)
            .arg("--dir=/tmp:tmp")
            .arg("--dir=/nix/store")
            .arg(usr_mount)
            .arg("--chdir=/box")
            .arg("--cg");
        Self::apply_limits(&mut isolate, limits);
        isolate.arg("--run").arg("--").arg(program);

        isolate.args(
            command
                .args
                .iter()
                .map(|arg| Self::expand_arg(arg, &substitutions)),
        );

        Ok(isolate.status()?)
    }

    fn copy_to_sandbox(&self, source: &Path) -> Result<String, Box<dyn std::error::Error>> {
        let source_name = source
            .file_name()
            .and_then(|name| name.to_str())
            .ok_or("invalid source filename")?;

        let sandbox_source = self.box_dir.join(source_name);

        fs::copy(source, sandbox_source)?;

        Ok(source_name.to_owned())
    }

    pub fn run_submission(
        &self,
        language: &LanguageConfig,
        source: &Path,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let source_name = self.copy_to_sandbox(source)?;
        let output_name = "main";
        let compile_limits = Limits {
            time: Some(Duration::from_secs(10)),
            wall_time: Some(Duration::from_secs(15)),
            processes: ProcessLimit::Max(10),
            memory_kib: Some(512 * 1024),
            ..Default::default()
        };

        for compile_command in &language.compile {
            let status = self.run(
                compile_command,
                language,
                &source_name,
                output_name,
                true,
                &compile_limits,
            )?;

            if !status.success() {
                return Err(format!("compilation failed: {status}").into());
            }
        }

        let runtime_limits = Limits {
            time: Some(Duration::from_secs(1)),
            wall_time: Some(Duration::from_secs(3)),
            processes: ProcessLimit::Max(10),
            memory_kib: Some(256 * 1024),
            ..Default::default()
        };

        let status = self.run(
            &language.run,
            language,
            &source_name,
            output_name,
            false,
            &runtime_limits,
        )?;
        // TODO: Use isolate metadata file to distinguish TLE, RE, signals, OOM, etc.
        if !status.success() {
            return Err(format!("execution failed: {status}").into());
        }

        Ok(())
    }

    fn cleanup(&mut self) {
        match self.isolate().arg("--cleanup").arg("--cg").status() {
            Ok(status) if !status.success() => {
                eprintln!("failed to clean up isolate box {}: {status}", self.box_id);
            }
            Err(error) => {
                eprintln!("failed to clean up isolate box {}: {error}", self.box_id);
            }
            _ => {}
        }
    }
}

impl Drop for IsolateBox {
    fn drop(&mut self) {
        self.cleanup();
    }
}
