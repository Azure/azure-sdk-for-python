import argparse
import asyncio
import os
import sys
import time
import signal
import shutil
import shlex
import subprocess
import urllib.request
from dataclasses import dataclass
from typing import IO, List, Optional

from azpysdk.proxy_ports import get_proxy_port_for_check
from ci_tools.functions import discover_targeted_packages
from ci_tools.variables import in_ci
from ci_tools.scenario.generation import build_whl_for_req, replace_dev_reqs
from ci_tools.logging import configure_logging, logger
from ci_tools.environment_exclusions import is_check_enabled, CHECK_DEFAULTS
from devtools_testutils.proxy_startup import prepare_local_tool

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ISOLATE_DIRS_TO_CLEAN: List[str] = []


@dataclass
class CheckResult:
    package: str
    check: str
    exit_code: int
    duration: float
    stdout: str
    stderr: str


@dataclass
class ProxyProcess:
    port: int
    process: subprocess.Popen
    log_handle: Optional[IO[str]]


PROXY_STATUS_SUFFIX = "/Info/Available"
PROXY_STARTUP_TIMEOUT = 60
BASE_PROXY_PORT = 5000


def _proxy_status_url(port: int) -> str:
    return f"http://localhost:{port}{PROXY_STATUS_SUFFIX}"


def _proxy_is_running(port: int) -> bool:
    try:
        with urllib.request.urlopen(_proxy_status_url(port), timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def _wait_for_proxy(port: int, timeout: int = PROXY_STARTUP_TIMEOUT) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _proxy_is_running(port):
            return True
        time.sleep(1)
    return _proxy_is_running(port)


def _wait_for_proxy_shutdown(port: int, timeout: int = 15) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not _proxy_is_running(port):
            return True
        time.sleep(0.5)
    return not _proxy_is_running(port)


def _start_proxy(port: int, tool_path: str) -> ProxyProcess:
    env = os.environ.copy()
    log_handle: Optional[IO[str]] = None

    if in_ci():
        log_path = os.path.join(root_dir, f"_proxy_log_{port}.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        log_handle = open(log_path, "a")
        assets_folder = os.path.join(root_dir, "l", f"proxy_{port}")
        os.makedirs(assets_folder, exist_ok=True)
        env["PROXY_ASSETS_FOLDER"] = assets_folder
        env["DOTNET_HOSTBUILDER__RELOADCONFIGONCHANGE"] = "false"

    command = shlex.split(
        f'{tool_path} start --storage-location="{root_dir}" -- --urls "http://localhost:{port}"'
    )
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0

    process = subprocess.Popen(
        command,
        stdout=log_handle or subprocess.DEVNULL,
        stderr=log_handle or subprocess.STDOUT,
        env=env,
        creationflags=creationflags,
    )

    if not _wait_for_proxy(port):
        process.terminate()
        if log_handle:
            log_handle.close()
        raise RuntimeError(f"Failed to start test proxy on port {port}")

    logger.info(f"Started test proxy on port {port}")
    return ProxyProcess(port=port, process=process, log_handle=log_handle)


def _stop_proxy_instances(instances: List[ProxyProcess]) -> None:
    for instance in instances:
        proc = instance.process
        if proc.poll() is None:
            try:
                if os.name == "nt" and hasattr(signal, "CTRL_BREAK_EVENT"):
                    proc.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    proc.send_signal(signal.SIGINT)
                proc.wait(timeout=20)
            except (ProcessLookupError, PermissionError):
                pass
            except (ValueError, OSError):
                pass
            except subprocess.TimeoutExpired:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
            except Exception:
                proc.terminate()
        if instance.log_handle:
            instance.log_handle.close()
        if _proxy_is_running(instance.port):
            if not _wait_for_proxy_shutdown(instance.port, timeout=10):
                logger.warning(f"Test proxy on port {instance.port} did not stop cleanly.")


def _cleanup_isolate_dirs() -> None:
    if not ISOLATE_DIRS_TO_CLEAN:
        return

    for path in ISOLATE_DIRS_TO_CLEAN:
        if not path:
            continue
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except Exception:
                logger.warning(f"Failed to remove isolate dir {path}")
    ISOLATE_DIRS_TO_CLEAN.clear()


def ensure_proxies_for_checks(checks: List[str]) -> List[ProxyProcess]:
    ports = sorted({get_proxy_port_for_check(check) for check in checks if check})
    if not ports:
        return []

    started: List[ProxyProcess] = []
    tool_path: Optional[str] = None

    try:
        for port in ports:
            if _proxy_is_running(port):
                logger.info(f"Test proxy already running on port {port}")
                continue
            if tool_path is None:
                tool_path = prepare_local_tool(root_dir)

            if tool_path is None:
                raise RuntimeError("Failed to prepare test proxy tool.")
            started.append(_start_proxy(port, tool_path))
    except Exception:
        _stop_proxy_instances(started)
        raise

    os.environ["PROXY_MANUAL_START"] = "1"
    return started


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


async def run_check(
    semaphore: asyncio.Semaphore,
    package: str,
    check: str,
    base_args: List[str],
    idx: int,
    total: int,
    proxy_port: int,
) -> CheckResult:
    """Run a single check (subprocess) within a concurrency semaphore, capturing output and timing.

    :param semaphore: Concurrency limiter used to bound concurrent checks.
    :type semaphore: asyncio.Semaphore
    :param package: Absolute path to the package directory used as the subprocess cwd.
    :type package: str
    :param check: The check (subcommand) name for the azpysdk CLI to invoke.
    :type check: str
    :param base_args: Common argument list prefix (e.g. ``[sys.executable, "-m", "azpysdk.main"]``).
    :type base_args: List[str]
    :param idx: Sequence number for logging (1-based index of this task).
    :type idx: int
    :param total: Total number of tasks (used for logging progress).
    :type total: int
    :param proxy_port: Dedicated proxy port assigned to this check instance.
    :type proxy_port: int
    :returns: A :class:`CheckResult` describing exit code, duration and captured output.
    :rtype: CheckResult
    """
    async with semaphore:
        start = time.time()
        cmd = base_args + [check, "--isolate", package]
        logger.info(f"[START {idx}/{total}] {check} :: {package}\nCMD: {' '.join(cmd)}")
        env = os.environ.copy()
        env["PROXY_URL"] = f"http://localhost:{proxy_port}"
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=package,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
        except Exception as ex:  # subprocess failed to launch
            logger.error(f"Failed to start check {check} for {package}: {ex}")
            return CheckResult(package, check, 127, 0.0, "", str(ex))

        stdout_b, stderr_b = await proc.communicate()
        duration = time.time() - start
        stdout = stdout_b.decode(errors="replace")
        stderr = stderr_b.decode(errors="replace")
        exit_code = proc.returncode or 0
        status = "OK" if exit_code == 0 else f"FAIL({exit_code})"
        logger.info(f"[END   {idx}/{total}] {check} :: {package} -> {status} in {duration:.2f}s")
        # Print captured output after completion to avoid interleaving
        header = f"===== OUTPUT: {check} :: {package} (exit {exit_code}) ====="
        trailer = "=" * len(header)
        if in_ci():
            print(f"##[group]{package} :: {check} :: {exit_code}")

        if stdout:
            print(header)
            print(_normalize_newlines(stdout).rstrip())
            print(trailer)
        if stderr:
            print(header.replace("OUTPUT", "STDERR"))
            print(_normalize_newlines(stderr).rstrip())
            print(trailer)

        if in_ci():
            print("##[endgroup]")

        # if we have any output collections to complete, do so now here

        # finally, we need to clean up any temp dirs created by --isolate
        if in_ci():
            package_name = os.path.basename(os.path.normpath(package))
            isolate_dir = os.path.join(root_dir, ".venv", package_name, f".venv_{check}")
            ISOLATE_DIRS_TO_CLEAN.append(isolate_dir)
        return CheckResult(package, check, exit_code, duration, stdout, stderr)


def summarize(results: List[CheckResult]) -> int:
    """Print a compact summary table and return the worst exit code.

    The function prints a human-readable table to stdout showing package, check, status and
    duration. It returns the highest (worst) exit code from the provided results.

    :param results: List of :class:`CheckResult` objects to summarize.
    :type results: List[CheckResult]
    :returns: The maximum exit code found in ``results`` (0 if all passed).
    :rtype: int
    """
    # Compute column widths
    pkg_w = max((len(r.package) for r in results), default=7)
    chk_w = max((len(r.check) for r in results), default=5)
    header = f"{'PACKAGE'.ljust(pkg_w)}  {'CHECK'.ljust(chk_w)}  STATUS  DURATION(s)"
    print("\n=== SUMMARY ===")
    print(header)
    print("-" * len(header))
    for r in sorted(results, key=lambda x: (x.exit_code != 0, x.package, x.check)):
        status = "OK" if r.exit_code == 0 else f"FAIL({r.exit_code})"
        print(f"{r.package.ljust(pkg_w)}  {r.check.ljust(chk_w)}  {status.ljust(8)}  {r.duration:>10.2f}")
    worst = max((r.exit_code for r in results), default=0)
    failed = [r for r in results if r.exit_code != 0]
    print(f"\nTotal checks: {len(results)} | Failed: {len(failed)} | Worst exit code: {worst}")
    return worst


async def run_all_checks(packages, checks, max_parallel, wheel_dir):
    """Run all checks for all packages concurrently and return the worst exit code.

    :param packages: Iterable of package paths to run checks against.
    :type packages: Iterable[str]
    :param checks: List of check names to execute for each package.
    :type checks: List[str]
    :param max_parallel: Maximum number of concurrent checks to run.
    :type max_parallel: int
    :param wheel_dir: The directory where wheels should be located and stored when built.
        In CI should correspond to `$(Build.ArtifactStagingDirectory)`.
    :type wheel_dir: str
    :returns: The worst exit code from all checks (0 if all passed).
    :rtype: int
    """
    base_args = [sys.executable, "-m", "azpysdk.main"]
    tasks = []
    semaphore = asyncio.Semaphore(max_parallel)
    combos = [(p, c) for p in packages for c in checks]
    scheduled: List[tuple] = []

    test_tools_path = os.path.join(root_dir, "eng", "test_tools.txt")
    dependency_tools_path = os.path.join(root_dir, "eng", "dependency_tools.txt")

    if in_ci():
        logger.info("Replacing relative requirements in eng/test_tools.txt with prebuilt wheels.")
        replace_dev_reqs(test_tools_path, root_dir, wheel_dir)

        logger.info("Replacing relative requirements in eng/dependency_tools.txt with prebuilt wheels.")
        replace_dev_reqs(dependency_tools_path, root_dir, wheel_dir)

        for pkg in packages:
            destination_dev_req = os.path.join(pkg, "dev_requirements.txt")

            logger.info(f"Replacing dev requirements w/ path {destination_dev_req}")
            if not os.path.exists(destination_dev_req):
                logger.info("No dev_requirements present.")
                with open(destination_dev_req, "w+") as file:
                    file.write("\n")

            replace_dev_reqs(destination_dev_req, pkg, wheel_dir)

    next_proxy_port = BASE_PROXY_PORT
    for package, check in combos:
        if not is_check_enabled(package, check, CHECK_DEFAULTS.get(check, True)):
            logger.warning(f"Skipping disabled check {check} for package {package}")
            continue
        scheduled.append((package, check, next_proxy_port))
        next_proxy_port += 1

    total = len(scheduled)

    for idx, (package, check, proxy_port) in enumerate(scheduled, start=1):
        tasks.append(
            asyncio.create_task(
                run_check(semaphore, package, check, base_args, idx, total or 1, proxy_port)
            )
        )

    # Handle Ctrl+C gracefully
    pending = set(tasks)
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt received. Cancelling running checks...")
        for t in pending:
            t.cancel()
        raise
    # Normalize exceptions
    norm_results: List[CheckResult] = []
    for res, (package, check, _) in zip(results, scheduled):
        if isinstance(res, CheckResult):
            norm_results.append(res)
        elif isinstance(res, Exception):
            norm_results.append(CheckResult(package, check, 99, 0.0, "", str(res)))
        else:
            norm_results.append(CheckResult(package, check, 98, 0.0, "", f"Unknown result type: {res}"))
    return summarize(norm_results)


def configure_interrupt_handling():
    """Install a SIGINT handler that triggers graceful shutdown.

    Registers a handler for SIGINT which raises :class:`KeyboardInterrupt` to allow
    the asyncio event loop to cancel tasks and subprocesses cleanly. On platforms or
    contexts where ``signal.signal`` is not supported (for example non-main threads),
    registration is skipped silently.

    :returns: None
    :rtype: None
    """

    # Ensure that a SIGINT propagates to asyncio tasks & subprocesses
    def handler(signum, frame):
        """Signal handler for SIGINT.

        Logs receipt of the signal and raises :class:`KeyboardInterrupt` to trigger
        graceful shutdown of asyncio tasks and subprocesses.

        :param signum: The numeric signal received (e.g. ``signal.SIGINT``).
        :type signum: int
        :param frame: Current stack frame when the signal was received (may be ``None``).
        :type frame: object
        :raises KeyboardInterrupt: Always raised to signal shutdown.
        """
        logger.warning(f"Received signal {signum}. Attempting graceful shutdown...")
        # Let asyncio loop raise KeyboardInterrupt
        raise KeyboardInterrupt

    try:
        signal.signal(signal.SIGINT, handler)
    except (ValueError, AttributeError):  # not supported on some platforms/threads
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
This script is the single point for all checks invoked by CI within this repo. It works in two phases.
    1. Identify which packages in the repo are in scope for this script invocation, based on a glob string and a service directory.
    2. Invoke one or multiple `checks` environments for each package identified as in scope.
In the case of an environment invoking `pytest`, results can be collected in a junit xml file, and test markers can be selected via --mark_arg.
""")

    parser.add_argument(
        "glob_string",
        nargs="?",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages."
            'Examples: All = "azure-*", Single = "azure-keyvault-keys", Targeted Multiple = "azure-keyvault-keys,azure-mgmt-resource"'
        ),
    )

    parser.add_argument(
        "--junitxml",
        dest="test_results",
        help=(
            "The output path for the test results file of invoked checks."
            'Example: --junitxml="junit/test-results.xml"'
        ),
    )

    parser.add_argument(
        "--mark_arg",
        dest="mark_arg",
        help=(
            'The complete argument for `pytest -m "<input>"`. This can be used to exclude or include specific pytest markers.'
            '--mark_arg="not cosmosEmulator"'
        ),
    )

    parser.add_argument("--disablecov", help=("Flag. Disables code coverage."), action="store_true")

    parser.add_argument(
        "--service",
        help=("Name of service directory (under sdk/) to test. Example: --service applicationinsights"),
    )

    parser.add_argument(
        "-c",
        "--checks",
        dest="checks_list",
        help="Specific set of named environments to execute",
    )

    parser.add_argument(
        "-w",
        "--wheel_dir",
        dest="wheel_dir",
        help="Location for prebuilt artifacts (if any)",
    )

    parser.add_argument(
        "-i",
        "--injected-packages",
        dest="injected_packages",
        default="",
        help="Comma or space-separated list of packages that should be installed prior to dev_requirements. If local path, should be absolute.",
    )

    parser.add_argument(
        "--filter-type",
        dest="filter_type",
        default="Build",
        help="Filter type to identify eligible packages. for e.g. packages filtered in Build can pass filter type as Build,",
        choices=["Build", "Docs", "Regression", "Omit_management", "None"],
    )

    parser.add_argument(
        "-d",
        "--dest-dir",
        dest="dest_dir",
        help="Location to generate any output files (if any). For e.g. APIView stub file",
    )

    parser.add_argument(
        "--max-parallel",
        dest="max_parallel",
        type=int,
        default=os.cpu_count() or 4,
        help="Maximum number of concurrent checks (default: number of CPU cores).",
    )

    parser.add_argument(
        "--disable-compatibility-filter",
        dest="disable_compatibility_filter",
        action="store_true",
        help="Flag to disable compatibility filter while discovering packages.",
    )

    args = parser.parse_args()

    configure_logging(args)

    # We need to support both CI builds of everything and individual service
    # folders. This logic allows us to do both.
    if args.service and args.service != "auto":
        service_dir = os.path.join("sdk", args.service)
        target_dir = os.path.join(root_dir, service_dir)
    else:
        target_dir = root_dir

    logger.info(f"Beginning discovery for {args.service} and root dir {root_dir}. Resolving to {target_dir}.")

    # ensure that recursive virtual envs aren't messed with by this call
    os.environ.pop("VIRTUAL_ENV", None)
    os.environ.pop("PYTHON_HOME", None)

    if args.filter_type == "None":
        args.filter_type = "Build"
        compatibility_filter = False
    else:
        compatibility_filter = not args.disable_compatibility_filter

    targeted_packages = discover_targeted_packages(
        args.glob_string, target_dir, "", args.filter_type, compatibility_filter
    )

    if len(targeted_packages) == 0:
        logger.info(f"No packages collected for targeting string {args.glob_string} and root dir {root_dir}. Exit 0.")
        exit(0)

    logger.info(f"Executing checks with the executable {sys.executable}.")
    logger.info(f"Packages targeted: {targeted_packages}")

    temp_wheel_dir = args.wheel_dir or os.path.join(root_dir, ".wheels")
    if args.wheel_dir:
        os.environ["PREBUILT_WHEEL_DIR"] = args.wheel_dir
    else:
        if not os.path.exists(temp_wheel_dir):
            os.makedirs(temp_wheel_dir)

    if in_ci():
        build_whl_for_req("eng/tools/azure-sdk-tools", root_dir, temp_wheel_dir)

    # so if we have checks whl,import_all and selected package paths `sdk/core/azure-core`, `sdk/storage/azure-storage-blob` we should
    # shell out to `azypysdk <checkname>` with cwd of the package directory, which is what is in `targeted_packages` array
    # each individual thread may need to re-invoke if they need to self-isolate themselves, but we don't have to worry about that.

    # Prepare check list
    raw_checks = (args.checks_list or "").split(",")
    checks = [c.strip() for c in raw_checks if c and c.strip()]
    if not checks:
        logger.error("No valid checks provided via -c/--checks.")
        sys.exit(2)

    logger.info(
        f"Running {len(checks)} check(s) across {len(targeted_packages)} packages (max_parallel={args.max_parallel})."
    )

    configure_interrupt_handling()
    proxy_processes: List[ProxyProcess] = []
    try:
        if in_ci():
            logger.info(f"Ensuring {len(checks)} test proxies are running for requested checks...")
            # proxy_processes = ensure_proxies_for_checks(checks)
        exit_code = asyncio.run(run_all_checks(targeted_packages, checks, args.max_parallel, temp_wheel_dir))
    except KeyboardInterrupt:
        logger.error("Aborted by user.")
        exit_code = 130
    finally:
        # _stop_proxy_instances(proxy_processes)
        _cleanup_isolate_dirs()
    sys.exit(exit_code)
