import argparse
import asyncio
import os
import logging
import sys
import time
import signal
from dataclasses import dataclass
from subprocess import check_call
from typing import List

from ci_tools.functions import discover_targeted_packages
from ci_tools.variables import in_ci
from ci_tools.scenario.generation import build_whl_for_req
from ci_tools.logging import configure_logging, logger

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

@dataclass
class CheckResult:
    package: str
    check: str
    exit_code: int
    duration: float
    stdout: str
    stderr: str


async def run_check(semaphore: asyncio.Semaphore, package: str, check: str, base_args: List[str], idx: int, total: int) -> CheckResult:
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
    :returns: A :class:`CheckResult` describing exit code, duration and captured output.
    :rtype: CheckResult
    """
    async with semaphore:
        start = time.time()
        cmd = base_args + [check, "--isolate", package]
        logger.info(f"[START {idx}/{total}] {check} :: {package}\nCMD: {' '.join(cmd)}")
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=package,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
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
        if stdout:
            print(header)
            print(stdout.rstrip())
            print(trailer)
        if stderr:
            print(header.replace('OUTPUT', 'STDERR'))
            print(stderr.rstrip())
            print(trailer)
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


async def run_all_checks(packages, checks, max_parallel):
    """Run all checks for all packages concurrently and return the worst exit code.

    :param packages: Iterable of package paths to run checks against.
    :type packages: Iterable[str]
    :param checks: List of check names to execute for each package.
    :type checks: List[str]
    :param max_parallel: Maximum number of concurrent checks to run.
    :type max_parallel: int
    :returns: The worst exit code from all checks (0 if all passed).
    :rtype: int
    """
    base_args = [sys.executable, "-m", "azpysdk.main"]
    tasks = []
    semaphore = asyncio.Semaphore(max_parallel)
    combos = [(p, c) for p in packages for c in checks]
    total = len(combos)
    for idx, (package, check) in enumerate(combos, start=1):
        tasks.append(asyncio.create_task(run_check(semaphore, package, check, base_args, idx, total)))

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
    for res, (package, check) in zip(results, combos):
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
        logging.warning(f"Received signal {signum}. Attempting graceful shutdown...")
        # Let asyncio loop raise KeyboardInterrupt
        raise KeyboardInterrupt

    try:
        signal.signal(signal.SIGINT, handler)
    except (ValueError, AttributeError):  # not supported on some platforms/threads
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
This script is the single point for all checks invoked by CI within this repo. It works in two phases.
    1. Identify which packages in the repo are in scope for this script invocation, based on a glob string and a service directory.
    2. Invoke one or multiple `checks` environments for each package identified as in scope.
In the case of an environment invoking `pytest`, results can be collected in a junit xml file, and test markers can be selected via --mark_arg.
"""
    )

    parser.add_argument(
        "glob_string",
        nargs="?",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages."
            'Examples: All = "azure-*", Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"'
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
        help="Location to generate any output files(if any). For e.g. apiview stub file",
    )

    parser.add_argument(
        "--max-parallel",
        dest="max_parallel",
        type=int,
        default=os.cpu_count() or 4,
        help="Maximum number of concurrent checks (default: number of CPU cores).",
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

    if args.filter_type == "None":
        args.filter_type = "Build"
        compatibility_filter = False
    else:
        compatibility_filter = True

    targeted_packages = discover_targeted_packages(
        args.glob_string, target_dir, "", args.filter_type, compatibility_filter
    )

    if len(targeted_packages) == 0:
        logger.info(f"No packages collected for targeting string {args.glob_string} and root dir {root_dir}. Exit 0.")
        exit(0)

    logger.info(f"Executing checks with the executable {sys.executable}.")
    logger.info(f"Packages targeted: {targeted_packages}")

    if args.wheel_dir:
        os.environ["PREBUILT_WHEEL_DIR"] = args.wheel_dir

    if not os.path.exists(os.path.join(root_dir, ".wheels")):
        os.makedirs(os.path.join(root_dir, ".wheels"))

    if in_ci():
        # prepare a build of eng/tools/azure-sdk-tools
        # todo: ensure that we honor this .wheels directory when replacing for dev reqs
        build_whl_for_req("eng/tools/azure-sdk-tools", root_dir, os.path.join(root_dir, ".wheels"))

    # so if we have checks whl,import_all and selected package paths `sdk/core/azure-core`, `sdk/storage/azure-storage-blob` we should
    # shell out to `azypysdk <checkname>` with cwd of the package directory, which is what is in `targeted_packages` array
    # each individual thread may need to re-invoke if they need to self-isolate themselves, but we don't have to worry about that.

    # Prepare check list
    raw_checks = (args.checks_list or "").split(",")
    checks = [c.strip() for c in raw_checks if c and c.strip()]
    if not checks:
        logger.error("No valid checks provided via -c/--checks.")
        sys.exit(2)

    logger.info(f"Running {len(checks)} checks across {len(targeted_packages)} packages (max_parallel={args.max_parallel}).")

    configure_interrupt_handling()
    try:
        exit_code = asyncio.run(run_all_checks(targeted_packages, checks, args.max_parallel))
    except KeyboardInterrupt:
        logger.error("Aborted by user.")
        exit_code = 130
    sys.exit(exit_code)
