//! Build-time check that the QueryPlanInterop files staged into the wheel were
//! compiled for the platform this wheel targets.
//!
//! Cargo runs this file before compiling the binding crate. It only does work
//! when a wheel build has staged QueryPlanInterop files (see
//! `azure_cosmos_build_backend.py`); an ordinary `cargo build` skips it.
//!
//! Why it exists: nothing about a `.dll`, `.so`, or `.dylib` filename says
//! which CPU it was built for. An x64 file and an ARM64 file are named
//! identically. If the wrong one is copied into an `azure/cosmos/.libs`
//! directory, the mistake is invisible until a customer installs that wheel
//! and the operating system refuses to load the library at run time. The
//! symptom is silent: the driver treats an unloadable library the same as a
//! missing one and quietly falls back to asking the gateway for query plans,
//! so the wheel looks fine and simply never delivers the feature it shipped
//! for.
//!
//! So this file reads each staged binary's own header, which does record the
//! CPU, and fails the build immediately on a mismatch.

use std::env;
use std::fs;
use std::path::Path;
use std::path::PathBuf;

mod query_plan_binary;

const SOURCE_DIRECTORY_ENV: &str = "AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR";
const STAGING_ACTIVE_ENV: &str = "AZURE_COSMOS_QUERYPLANINTEROP_STAGING_ACTIVE";

fn primary_library_name(target_os: &str) -> &'static str {
    match target_os {
        "windows" => "Cosmos.QueryPlanInterop.dll",
        "linux" => "libqueryplaninterop.so",
        "macos" => "libqueryplaninterop.dylib",
        unsupported => panic!("QueryPlanInterop packaging is not supported on {unsupported}"),
    }
}

fn is_native_library(path: &Path, target_os: &str) -> bool {
    let Some(name) = path.file_name().and_then(|value| value.to_str()) else {
        return false;
    };
    match target_os {
        "windows" => name.to_ascii_lowercase().ends_with(".dll"),
        "linux" => name.ends_with(".so") || name.contains(".so."),
        "macos" => name.ends_with(".dylib"),
        _ => false,
    }
}

fn main() {
    println!("cargo:rerun-if-env-changed={SOURCE_DIRECTORY_ENV}");
    println!("cargo:rerun-if-env-changed={STAGING_ACTIVE_ENV}");

    let Some(source_directory) = env::var_os(SOURCE_DIRECTORY_ENV).map(PathBuf::from) else {
        return;
    };
    if env::var_os(STAGING_ACTIVE_ENV).is_none() {
        panic!(
            "{SOURCE_DIRECTORY_ENV} is set, but wheel staging is not active; build through the \
             configured PEP 517 backend instead of invoking Maturin directly"
        );
    }
    let target_os =
        env::var("CARGO_CFG_TARGET_OS").expect("Cargo must provide CARGO_CFG_TARGET_OS");
    let target_arch =
        env::var("CARGO_CFG_TARGET_ARCH").expect("Cargo must provide CARGO_CFG_TARGET_ARCH");
    let target_pointer_width = env::var("CARGO_CFG_TARGET_POINTER_WIDTH")
        .expect("Cargo must provide CARGO_CFG_TARGET_POINTER_WIDTH");
    let primary_library = primary_library_name(&target_os);
    let primary_path = source_directory.join(primary_library);
    if !primary_path.is_file() {
        panic!(
            "{SOURCE_DIRECTORY_ENV} must contain the target library {}",
            primary_path.display()
        );
    }
    for entry in fs::read_dir(&source_directory)
        .unwrap_or_else(|error| panic!("failed to read {}: {error}", source_directory.display()))
    {
        let path = entry
            .expect("failed to read QueryPlanInterop directory entry")
            .path();
        if path.is_file() && is_native_library(&path, &target_os) {
            query_plan_binary::validate_binary_architecture(
                &path,
                &target_os,
                &target_arch,
                &target_pointer_width,
            )
            .unwrap_or_else(|error| panic!("{error}"));
        }
    }

    println!("cargo:rerun-if-changed={}", source_directory.display());
}
