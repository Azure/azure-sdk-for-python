//! Choose the source-commit labels that `build.rs` embeds in the binding.
//!
//! Support reads them from `_rust.__python_commit__` and
//! `_rust.__rust_driver_commit__` to tell which sources a wheel was built from.

pub const DRIVER_PACKAGE: &str = "azure_data_cosmos_driver";
pub const UNKNOWN: &str = "unknown";
pub const LOCAL: &str = "local";

/// An explicit value wins. Otherwise use the commit Azure Pipelines is building.
pub fn python_commit(explicit: Option<&str>, build_source_version: Option<&str>) -> String {
    [explicit, build_source_version]
        .into_iter()
        .flatten()
        .map(str::trim)
        .find(|value| !value.is_empty())
        .unwrap_or(UNKNOWN)
        .to_string()
}

/// An explicit value wins. Otherwise read the driver's pinned git commit from
/// `Cargo.lock`. A driver entry with no `source` is a local path build.
pub fn driver_commit(explicit: Option<&str>, cargo_lock: Option<&str>) -> String {
    if let Some(value) = explicit.map(str::trim).filter(|value| !value.is_empty()) {
        return value.to_string();
    }
    let Some(cargo_lock) = cargo_lock else {
        return UNKNOWN.to_string();
    };
    for package in cargo_lock.split("[[package]]").skip(1) {
        if field(package, "name") != Some(DRIVER_PACKAGE) {
            continue;
        }
        return match field(package, "source") {
            None => LOCAL.to_string(),
            Some(source) => git_commit(source).unwrap_or(UNKNOWN).to_string(),
        };
    }
    UNKNOWN.to_string()
}

fn field<'a>(package: &'a str, key: &str) -> Option<&'a str> {
    package.lines().find_map(|line| {
        let (name, value) = line.split_once('=')?;
        (name.trim() == key).then(|| value.trim().trim_matches('"'))
    })
}

fn git_commit(source: &str) -> Option<&str> {
    let commit = source.strip_prefix("git+")?.rsplit_once('#')?.1;
    (commit.len() == 40 && commit.bytes().all(|byte| byte.is_ascii_hexdigit())).then_some(commit)
}

#[cfg(test)]
mod tests {
    use super::*;

    const SHA: &str = "b485409baf6e24ce198b028fb6d1c5a54a0e6d4c";

    fn lock(driver_source: Option<&str>) -> String {
        let source = driver_source
            .map(|value| format!("source = \"{value}\"\n"))
            .unwrap_or_default();
        format!(
            "version = 4\n\n[[package]]\nname = \"azure_data_cosmos_driver_macros\"\n\
             version = \"1.0.0\"\nsource = \"git+https://example/repo#{}\"\n\n\
             [[package]]\nname = \"{DRIVER_PACKAGE}\"\nversion = \"1.1.0\"\n{source}\
             dependencies = [\n \"serde\",\n]\n",
            "0".repeat(40)
        )
    }

    #[test]
    fn driver_commit_comes_from_the_pinned_git_source() {
        let source = format!("git+https://github.com/Azure/azure-sdk-for-rust?rev={SHA}#{SHA}");
        assert_eq!(driver_commit(None, Some(&lock(Some(&source)))), SHA);
    }

    #[test]
    fn driver_commit_reports_local_and_unknown_sources() {
        assert_eq!(driver_commit(None, Some(&lock(None))), LOCAL);
        let registry = "registry+https://github.com/rust-lang/crates.io-index";
        assert_eq!(driver_commit(None, Some(&lock(Some(registry)))), UNKNOWN);
        assert_eq!(driver_commit(None, Some("version = 4\n")), UNKNOWN);
        assert_eq!(driver_commit(None, None), UNKNOWN);
    }

    #[test]
    fn explicit_values_win_and_blank_values_are_ignored() {
        assert_eq!(driver_commit(Some("abc"), Some(&lock(None))), "abc");
        assert_eq!(driver_commit(Some(" "), Some(&lock(None))), LOCAL);
        assert_eq!(python_commit(Some("abc"), Some("def")), "abc");
        assert_eq!(python_commit(Some(""), Some("def")), "def");
        assert_eq!(python_commit(None, None), UNKNOWN);
    }
}
