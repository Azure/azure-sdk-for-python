//! Reads the CPU recorded inside a compiled library file.
//!
//! Every compiled library starts with a header that names the CPU it was built
//! for. The three operating systems use three different header formats: PE on
//! Windows, ELF on Linux, Mach-O on macOS. This file reads all three and
//! reports the CPU as one value the build script can compare against the CPU
//! Cargo was told to target.
//!
//! It is used by `build.rs` at build time and compiled again into the crate's
//! test build so the readers themselves can be tested.
//!
//! Without it the build would have to trust that whoever supplied the
//! QueryPlanInterop files picked the right ones by hand, and a wrong pick would
//! only surface as a customer whose queries never use local planning.

use std::fs;
use std::path::Path;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum BinaryArchitecture {
    X86,
    X86_64,
    Arm,
    Aarch64,
}

pub fn validate_binary_architecture(
    path: &Path,
    target_os: &str,
    target_arch: &str,
    target_pointer_width: &str,
) -> Result<(), String> {
    let expected = target_architecture(target_arch)
        .ok_or_else(|| format!("unsupported QueryPlanInterop target architecture {target_arch}"))?;
    let bytes =
        fs::read(path).map_err(|error| format!("failed to read {}: {error}", path.display()))?;
    let architectures = detect_architectures(&bytes, target_os)?;
    if target_os == "linux" {
        let (_, binary_pointer_width) = detect_elf_architecture(&bytes)?;
        let expected_pointer_width = target_pointer_width.parse::<u8>().map_err(|error| {
            format!("invalid Cargo target pointer width {target_pointer_width}: {error}")
        })?;
        if binary_pointer_width != expected_pointer_width {
            return Err(format!(
                "{} is an ELFCLASS{binary_pointer_width} binary, not the Cargo target's \
                 {expected_pointer_width}-bit class",
                path.display()
            ));
        }
    }
    if architectures.contains(&expected) {
        Ok(())
    } else {
        Err(format!(
            "{} contains architectures {architectures:?}, not the Cargo target {target_arch}",
            path.display()
        ))
    }
}

fn target_architecture(target_arch: &str) -> Option<BinaryArchitecture> {
    match target_arch {
        "x86" => Some(BinaryArchitecture::X86),
        "x86_64" => Some(BinaryArchitecture::X86_64),
        "arm" => Some(BinaryArchitecture::Arm),
        "aarch64" => Some(BinaryArchitecture::Aarch64),
        _ => None,
    }
}

fn detect_architectures(bytes: &[u8], target_os: &str) -> Result<Vec<BinaryArchitecture>, String> {
    match target_os {
        "windows" => detect_pe_architecture(bytes).map(|architecture| vec![architecture]),
        "linux" => detect_elf_architecture(bytes).map(|(architecture, _)| vec![architecture]),
        "macos" => detect_mach_o_architectures(bytes),
        unsupported => Err(format!(
            "QueryPlanInterop binary inspection is not supported on {unsupported}"
        )),
    }
}

fn detect_pe_architecture(bytes: &[u8]) -> Result<BinaryArchitecture, String> {
    if bytes.get(..2) != Some(b"MZ") || bytes.len() < 0x40 {
        return Err("QueryPlanInterop DLL does not have a valid DOS header".to_string());
    }
    let pe_offset = read_u32(bytes, 0x3c, Endianness::Little)? as usize;
    if bytes.get(pe_offset..pe_offset + 4) != Some(b"PE\0\0") {
        return Err("QueryPlanInterop DLL does not have a valid PE header".to_string());
    }
    let machine = read_u16(bytes, pe_offset + 4, Endianness::Little)?;
    match machine {
        0x014c => Ok(BinaryArchitecture::X86),
        0x8664 => Ok(BinaryArchitecture::X86_64),
        0x01c0 | 0x01c4 => Ok(BinaryArchitecture::Arm),
        0xaa64 => Ok(BinaryArchitecture::Aarch64),
        _ => Err(format!(
            "QueryPlanInterop DLL has unsupported PE machine 0x{machine:04x}"
        )),
    }
}

fn detect_elf_architecture(bytes: &[u8]) -> Result<(BinaryArchitecture, u8), String> {
    if bytes.get(..4) != Some(b"\x7fELF") || bytes.len() < 20 {
        return Err("QueryPlanInterop library does not have a valid ELF header".to_string());
    }
    let pointer_width = match bytes[4] {
        1 => 32,
        2 => 64,
        value => return Err(format!("ELF header has unsupported class {value}")),
    };
    let endianness = match bytes[5] {
        1 => Endianness::Little,
        2 => Endianness::Big,
        value => return Err(format!("ELF header has unsupported data encoding {value}")),
    };
    let machine = read_u16(bytes, 18, endianness)?;
    match machine {
        3 => Ok((BinaryArchitecture::X86, pointer_width)),
        62 => Ok((BinaryArchitecture::X86_64, pointer_width)),
        40 => Ok((BinaryArchitecture::Arm, pointer_width)),
        183 => Ok((BinaryArchitecture::Aarch64, pointer_width)),
        _ => Err(format!(
            "QueryPlanInterop library has unsupported ELF machine {machine}"
        )),
    }
}

fn detect_mach_o_architectures(bytes: &[u8]) -> Result<Vec<BinaryArchitecture>, String> {
    let magic = bytes
        .get(..4)
        .ok_or_else(|| "QueryPlanInterop library has a truncated Mach-O header".to_string())?;
    match magic {
        [0xfe, 0xed, 0xfa, 0xce] | [0xfe, 0xed, 0xfa, 0xcf] => {
            mach_o_cpu(bytes, Endianness::Big).map(|architecture| vec![architecture])
        }
        [0xce, 0xfa, 0xed, 0xfe] | [0xcf, 0xfa, 0xed, 0xfe] => {
            mach_o_cpu(bytes, Endianness::Little).map(|architecture| vec![architecture])
        }
        [0xca, 0xfe, 0xba, 0xbe] => detect_fat_mach_o(bytes, Endianness::Big, 20),
        [0xbe, 0xba, 0xfe, 0xca] => detect_fat_mach_o(bytes, Endianness::Little, 20),
        [0xca, 0xfe, 0xba, 0xbf] => detect_fat_mach_o(bytes, Endianness::Big, 32),
        [0xbf, 0xba, 0xfe, 0xca] => detect_fat_mach_o(bytes, Endianness::Little, 32),
        _ => Err("QueryPlanInterop library does not have a valid Mach-O header".to_string()),
    }
}

fn mach_o_cpu(bytes: &[u8], endianness: Endianness) -> Result<BinaryArchitecture, String> {
    let cpu_type = read_u32(bytes, 4, endianness)?;
    mach_o_architecture(cpu_type)
}

fn detect_fat_mach_o(
    bytes: &[u8],
    endianness: Endianness,
    entry_size: usize,
) -> Result<Vec<BinaryArchitecture>, String> {
    let architecture_count = read_u32(bytes, 4, endianness)? as usize;
    if architecture_count == 0 || architecture_count > 64 {
        return Err(format!(
            "QueryPlanInterop universal Mach-O has invalid architecture count {architecture_count}"
        ));
    }
    let required_length = 8usize
        .checked_add(architecture_count.saturating_mul(entry_size))
        .ok_or_else(|| "QueryPlanInterop universal Mach-O header is too large".to_string())?;
    if bytes.len() < required_length {
        return Err("QueryPlanInterop universal Mach-O header is truncated".to_string());
    }

    let mut architectures = Vec::with_capacity(architecture_count);
    for index in 0..architecture_count {
        let cpu_type = read_u32(bytes, 8 + index * entry_size, endianness)?;
        let architecture = mach_o_architecture(cpu_type)?;
        if !architectures.contains(&architecture) {
            architectures.push(architecture);
        }
    }
    Ok(architectures)
}

fn mach_o_architecture(cpu_type: u32) -> Result<BinaryArchitecture, String> {
    match cpu_type {
        7 => Ok(BinaryArchitecture::X86),
        0x0100_0007 => Ok(BinaryArchitecture::X86_64),
        12 => Ok(BinaryArchitecture::Arm),
        0x0100_000c => Ok(BinaryArchitecture::Aarch64),
        _ => Err(format!(
            "QueryPlanInterop library has unsupported Mach-O CPU type 0x{cpu_type:08x}"
        )),
    }
}

#[derive(Clone, Copy)]
enum Endianness {
    Little,
    Big,
}

fn read_u16(bytes: &[u8], offset: usize, endianness: Endianness) -> Result<u16, String> {
    let value: [u8; 2] = bytes
        .get(offset..offset + 2)
        .ok_or_else(|| "QueryPlanInterop binary header is truncated".to_string())?
        .try_into()
        .expect("slice length is checked");
    Ok(match endianness {
        Endianness::Little => u16::from_le_bytes(value),
        Endianness::Big => u16::from_be_bytes(value),
    })
}

fn read_u32(bytes: &[u8], offset: usize, endianness: Endianness) -> Result<u32, String> {
    let value: [u8; 4] = bytes
        .get(offset..offset + 4)
        .ok_or_else(|| "QueryPlanInterop binary header is truncated".to_string())?
        .try_into()
        .expect("slice length is checked");
    Ok(match endianness {
        Endianness::Little => u32::from_le_bytes(value),
        Endianness::Big => u32::from_be_bytes(value),
    })
}

#[cfg(test)]
mod tests {
    //! Checks the header readers against hand-built byte sequences.
    //!
    //! Real libraries for other CPUs and other operating systems are not
    //! available on the machine running the build, so each test writes the few
    //! header bytes that name a CPU and nothing else. That is enough, because
    //! those bytes are all the readers look at.
    //!
    //! Without these, the only way to find out that a reader was wrong would be
    //! a release that shipped a library no customer's machine could load.

    use super::*;

    #[test]
    fn detects_pe_x86_64() {
        let mut bytes = vec![0; 0x86];
        bytes[..2].copy_from_slice(b"MZ");
        bytes[0x3c..0x40].copy_from_slice(&0x80u32.to_le_bytes());
        bytes[0x80..0x84].copy_from_slice(b"PE\0\0");
        bytes[0x84..0x86].copy_from_slice(&0x8664u16.to_le_bytes());

        assert_eq!(
            detect_architectures(&bytes, "windows").unwrap(),
            vec![BinaryArchitecture::X86_64]
        );
    }

    #[test]
    fn detects_big_endian_elf_aarch64() {
        let mut bytes = vec![0; 20];
        bytes[..4].copy_from_slice(b"\x7fELF");
        bytes[4] = 2;
        bytes[5] = 2;
        bytes[18..20].copy_from_slice(&183u16.to_be_bytes());

        assert_eq!(
            detect_architectures(&bytes, "linux").unwrap(),
            vec![BinaryArchitecture::Aarch64]
        );
    }

    #[test]
    fn detects_thin_mach_o_x86_64() {
        let mut bytes = vec![0; 8];
        bytes[..4].copy_from_slice(&[0xcf, 0xfa, 0xed, 0xfe]);
        bytes[4..8].copy_from_slice(&0x0100_0007u32.to_le_bytes());

        assert_eq!(
            detect_architectures(&bytes, "macos").unwrap(),
            vec![BinaryArchitecture::X86_64]
        );
    }

    #[test]
    fn detects_universal_mach_o_architectures() {
        let mut bytes = vec![0; 72];
        bytes[..4].copy_from_slice(&[0xca, 0xfe, 0xba, 0xbf]);
        bytes[4..8].copy_from_slice(&2u32.to_be_bytes());
        bytes[8..12].copy_from_slice(&0x0100_0007u32.to_be_bytes());
        bytes[40..44].copy_from_slice(&0x0100_000cu32.to_be_bytes());

        assert_eq!(
            detect_architectures(&bytes, "macos").unwrap(),
            vec![BinaryArchitecture::X86_64, BinaryArchitecture::Aarch64]
        );
    }

    #[test]
    fn rejects_architecture_mismatch() {
        let mut bytes = vec![0; 20];
        bytes[..4].copy_from_slice(b"\x7fELF");
        bytes[4] = 2;
        bytes[5] = 1;
        bytes[18..20].copy_from_slice(&62u16.to_le_bytes());

        let architectures = detect_architectures(&bytes, "linux").unwrap();
        assert!(!architectures.contains(&BinaryArchitecture::Aarch64));
    }

    #[test]
    fn validates_binary_against_cargo_target_architecture() {
        let mut bytes = vec![0; 0x86];
        bytes[..2].copy_from_slice(b"MZ");
        bytes[0x3c..0x40].copy_from_slice(&0x80u32.to_le_bytes());
        bytes[0x80..0x84].copy_from_slice(b"PE\0\0");
        bytes[0x84..0x86].copy_from_slice(&0x8664u16.to_le_bytes());
        let path =
            std::env::temp_dir().join(format!("query-plan-binary-test-{}", std::process::id()));
        fs::write(&path, bytes).unwrap();

        validate_binary_architecture(&path, "windows", "x86_64", "64").unwrap();
        let error = validate_binary_architecture(&path, "windows", "aarch64", "64").unwrap_err();
        assert!(error.contains("not the Cargo target aarch64"));

        fs::remove_file(path).unwrap();
    }

    #[test]
    fn rejects_elf_pointer_width_mismatch() {
        let mut bytes = vec![0; 20];
        bytes[..4].copy_from_slice(b"\x7fELF");
        bytes[4] = 1;
        bytes[5] = 1;
        bytes[18..20].copy_from_slice(&62u16.to_le_bytes());
        let path =
            std::env::temp_dir().join(format!("query-plan-elf-class-test-{}", std::process::id()));
        fs::write(&path, bytes).unwrap();

        let error = validate_binary_architecture(&path, "linux", "x86_64", "64").unwrap_err();
        assert!(error.contains("ELFCLASS32"));

        fs::remove_file(path).unwrap();
    }
}
