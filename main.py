#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from pax_simulator.config import load_config
from pax_simulator.models import UserProfile
from pax_simulator.runner import SimulatorRunner


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    common.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    common.add_argument("--domain", help="Specify website domain (e.g., uat02.uwingame.fun)")

    parser = argparse.ArgumentParser(
        description="PAX User Simulator - Selenium automation for uwin registration and behavior simulation",
        parents=[common],
    )
    sub = parser.add_subparsers(dest="command", required=True)

    register_cmd = sub.add_parser("register", help="Register a new user", parents=[common])
    register_cmd.add_argument("--email", help="Custom email")
    register_cmd.add_argument("--username", help="Custom username")
    register_cmd.add_argument("--password", help="Custom password")
    register_cmd.add_argument("--referral", help="Referral code")

    sub.add_parser("simulate", help="Simulate browsing behavior on homepage", parents=[common])
    sub.add_parser("full", help="Register a user then simulate behavior", parents=[common])

    batch_cmd = sub.add_parser("batch", help="Batch register users from a file list", parents=[common])
    batch_cmd.add_argument("--file", help="Path to the user list file (defaults to data/{domain}.txt)")

    inspect_cmd = sub.add_parser("inspect", help="Print visible form elements on register page", parents=[common])
    inspect_cmd.add_argument("--wait", type=int, default=8, help="Seconds to wait after page load")

    return parser


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    setup_logging(args.verbose)

    config = load_config()
    if args.headless:
        config.browser.headless = True
    if args.domain:
        domain = args.domain.strip()
        if not domain.startswith(("http://", "https://")):
            config.site.base_url = f"https://{domain}"
        else:
            config.site.base_url = domain

    runner = SimulatorRunner(config)
    exit_code = 0

    try:
        if args.command == "register":
            user = None
            if any([args.email, args.username, args.password, args.referral]):
                factory_email = args.email or "custom@example.com"
                user = UserProfile(
                    email=factory_email,
                    username=args.username or factory_email.split("@")[0],
                    password=args.password or "TestPass123!",
                    referral_code=args.referral or config.registration.referral_code,
                )
            result = runner.register_user(user)
            print(f"Success: {result.success}")
            print(f"User: {result.user.username} / {result.user.email}")
            if result.message:
                print(f"Message: {result.message}")
            exit_code = 0 if result.success else 1

        elif args.command == "simulate":
            runner.simulate_behavior()

        elif args.command == "full":
            result = runner.register_and_simulate()
            print(f"Success: {result.success}")
            print(f"User: {result.user.username} / {result.user.email}")
            exit_code = 0 if result.success else 1

        elif args.command == "batch":
            from urllib.parse import urlparse
            parsed = urlparse(config.site.base_url)
            domain_name = parsed.netloc or parsed.path
            domain_name = domain_name.split(":")[0]  # remove port if any
            
            file_path = args.file
            if not file_path:
                file_path = ROOT / "data" / f"{domain_name}.txt"
            else:
                file_path = Path(file_path)
                
            runner.run_batch(file_path)

        elif args.command == "inspect":
            from pax_simulator.utils.inspect import inspect_register_page

            inspect_register_page(wait_sec=args.wait, config=config)

    finally:
        runner.close()

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
