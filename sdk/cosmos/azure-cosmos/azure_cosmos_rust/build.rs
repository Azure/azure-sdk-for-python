//! Embed supplied source-commit labels and check staged QueryPlanInterop binaries.
//!
//! Cargo runs this before compiling the binding. Commit labels are always set;
//! `build_commit.rs` says where each comes from. Binary checks run only when a
//! source directory is supplied and the wheel backend lists the files it staged.
//! The backend alone decides which files are native libraries; this file checks
//! exactly the files it lists.
//!
//! Why it exists: nothing about a `.dll`, `.so`, or `.dylib` filename says
//! which CPU it was built for. An x64 file and an ARM64 file are named
//! identically. Inspecting their headers catches an architecture mismatch at
//! build time, rather than relying on a later load attempt to discover it.
//!
//! So this file reads each staged binary's own header, which does record the
//! CPU, and fails the build on a mismatch. This does not load the library or
//! prove that its dependencies, exports, or runtime behavior are compatible.

use std::env;
use std::fs;
use std::path::PathBuf;

mod build_commit;
mod query_plan_binary;

const SOURCE_DIRECTORY_ENV: &str = "AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR";
const STAGED_FILES_ENV: &str = "AZURE_COSMOS_QUERYPLANINTEROP_STAGED_FILES";
const PYTHON_COMMIT_ENV: &str = "AZURE_COSMOS_BUILD_PYTHON_COMMIT";
const RUST_DRIVER_COMMIT_ENV: &str = "AZURE_COSMOS_BUILD_RUST_DRIVER_COMMIT";
// Azure Pipelines sets this to the commit being built.
const BUILD_SOURCE_VERSION_ENV: &str = "BUILD_SOURCEVERSION";

fn primary_library_name(target_os: &str) -> &'static str {
    match target_os {
        "windows" => "Cosmos.QueryPlanInterop.dll",
        "linux" => "libqueryplaninterop.so",
        "macos" => "libqueryplaninterop.dylib",
        unsupported => panic!("QueryPlanInterop packaging is not supported on {unsupported}"),
    }
}

// The workspace lock file sits above the binding crate, also in a source distribution.
fn find_cargo_lock() -> Option<PathBuf> {
    let manifest_directory = PathBuf::from(env::var_os("CARGO_MANIFEST_DIR")?);
    manifest_directory
        .ancestors()
        .map(|directory| directory.join("Cargo.lock"))
        .find(|path| path.is_file())
}

fn main() {
    // Labels identify the sources by commit; they do not detect uncommitted edits.
    let cargo_lock = find_cargo_lock();
    if let Some(path) = &cargo_lock {
        println!("cargo:rerun-if-changed={}", path.display());
    }
    for variable in [PYTHON_COMMIT_ENV, RUST_DRIVER_COMMIT_ENV, BUILD_SOURCE_VERSION_ENV] {
        println!("cargo:rerun-if-env-changed={variable}");
    }
    let python_commit = build_commit::python_commit(
        env::var(PYTHON_COMMIT_ENV).ok().as_deref(),
        env::var(BUILD_SOURCE_VERSION_ENV).ok().as_deref(),
    );
    let driver_commit = build_commit::driver_commit(
        env::var(RUST_DRIVER_COMMIT_ENV).ok().as_deref(),
        cargo_lock.and_then(|path| fs::read_to_string(path).ok()).as_deref(),
    );
    println!("cargo:rustc-env={PYTHON_COMMIT_ENV}={python_commit}");
    println!("cargo:rustc-env={RUST_DRIVER_COMMIT_ENV}={driver_commit}");

    println!("cargo:rerun-if-env-changed={SOURCE_DIRECTORY_ENV}");
    println!("cargo:rerun-if-env-changed={STAGED_FILES_ENV}");

    let Some(source_directory) = env::var_os(SOURCE_DIRECTORY_ENV).map(PathBuf::from) else {
        return;
    };
    let Ok(staged_files) = env::var(STAGED_FILES_ENV) else {
        panic!(
            "{SOURCE_DIRECTORY_ENV} is set, but wheel staging is not active; build through the \
             configured PEP 517 backend instead of invoking Maturin directly"
        );
    };
    let staged_files: Vec<&str> = staged_files.split('\n').collect();
    let target_os =
        env::var("CARGO_CFG_TARGET_OS").expect("Cargo must provide CARGO_CFG_TARGET_OS");
    let target_arch =
        env::var("CARGO_CFG_TARGET_ARCH").expect("Cargo must provide CARGO_CFG_TARGET_ARCH");
    let target_pointer_width = env::var("CARGO_CFG_TARGET_POINTER_WIDTH")
        .expect("Cargo must provide CARGO_CFG_TARGET_POINTER_WIDTH");
    let primary_library = primary_library_name(&target_os);
    if !staged_files.contains(&primary_library) {
        panic!(
            "{SOURCE_DIRECTORY_ENV} must contain the target library {primary_library}; \
             staged files: {staged_files:?}"
        );
    }
    for name in staged_files {
        let path = source_directory.join(name);
        if !path.is_file() {
            panic!(
                "staged QueryPlanInterop file {} does not exist",
                path.display()
            );
        }
        query_plan_binary::validate_binary_architecture(
            &path,
            &target_os,
            &target_arch,
            &target_pointer_width,
        )
        .unwrap_or_else(|error| panic!("{error}"));
    }

    println!("cargo:rerun-if-changed={}", source_directory.display());
}
