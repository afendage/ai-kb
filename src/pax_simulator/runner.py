from __future__ import annotations

import json
import logging
from pathlib import Path

from pax_simulator.actions.user_behavior import UserBehaviorSimulator
from pax_simulator.config import AppConfig, load_config
from pax_simulator.driver import DriverFactory
from pax_simulator.models import RegistrationResult, UserProfile
from pax_simulator.pages.register import RegisterPage
from pax_simulator.utils.random_data import UserDataFactory

logger = logging.getLogger(__name__)
ARTIFACTS_DIR = Path("artifacts")


class SimulatorRunner:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or load_config()
        self.driver = DriverFactory.create(self.config.browser)

    def close(self) -> None:
        if self.driver:
            self.driver.quit()

    def register_user(self, user: UserProfile | None = None) -> RegistrationResult:
        user = user or UserDataFactory(self.config.registration).create()
        page = RegisterPage(self.driver)
        result = page.register(self.config.site.register_url, user)
        self._persist_user(result)
        return result

    def simulate_behavior(self) -> None:
        simulator = UserBehaviorSimulator(self.driver, self.config)
        simulator.run()

    def register_and_simulate(self, user: UserProfile | None = None) -> RegistrationResult:
        result = self.register_user(user)
        if result.success:
            self.simulate_behavior()
        return result

    def _persist_user(self, result: RegistrationResult) -> None:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = ARTIFACTS_DIR / "users.jsonl"
        payload = {
            "success": result.success,
            "message": result.message,
            "email": result.user.email,
            "username": result.user.username,
            "password": result.user.password,
            "referral_code": result.user.referral_code,
            "created_at": result.user.created_at,
            "screenshot": result.screenshot_path,
        }
        with output_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
        logger.info("Saved user record to %s", output_path)

    def run_batch(self, file_path: Path) -> None:
        if not file_path.exists():
            logger.error("Batch file %s does not exist", file_path)
            print(f"Error: Batch file {file_path} does not exist.")
            return

        # Read usernames and their statuses
        users_to_process = []
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue
                parts = stripped.split(",")
                username = parts[0].strip()
                status = parts[1].strip() if len(parts) > 1 else None
                users_to_process.append((username, status))

        unprocessed = [u for u in users_to_process if not u[1]]
        if not unprocessed:
            logger.info("All users in %s are already processed.", file_path)
            print("All users are already processed.")
            return

        logger.info("Found %d unprocessed users out of %d total.", len(unprocessed), len(users_to_process))
        print(f"Starting batch registration: {len(unprocessed)} users to process.")

        for i, (username, _) in enumerate(unprocessed, 1):
            print(f"[{i}/{len(unprocessed)}] Processing user: {username}")
            
            # Ensure driver is alive and responsive
            try:
                self.driver.title
            except Exception:
                logger.info("Driver is not responding, recreating driver...")
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = DriverFactory.create(self.config.browser)

            # Clear cookies and storage for a clean slate
            try:
                self.driver.get(self.config.site.register_url)
                self.driver.delete_all_cookies()
                self.driver.execute_script("window.localStorage.clear();")
                self.driver.execute_script("window.sessionStorage.clear();")
            except Exception as e:
                logger.warning("Failed to clear cookies/storage: %s", e)

            # Generate random password and email for this username
            factory = UserDataFactory(self.config.registration)
            password = factory._generate_password(self.config.registration.password_length)
            email = f"{username}@{self.config.registration.email_domain}"
            user = UserProfile(email=email, username=username, password=password)

            # Run registration
            try:
                page = RegisterPage(self.driver)
                result = page.register(self.config.site.register_url, user)
                self._persist_user(result)
                
                if result.success:
                    status_str = "processed"
                    print(f"  -> Success: {username}")
                else:
                    # If it failed due to captcha or other error, mark it
                    reason = result.message or "failed"
                    status_str = f"failed:{reason}"
                    print(f"  -> Failed: {username} ({reason})")
                
                # Update status in file immediately
                self._update_file_status(file_path, username, status_str)
                
            except Exception as e:
                # If we get an invalid session id or connection reset, it means the browser crashed or was killed.
                # Do NOT mark this user as error/failed in the file, because they might have actually succeeded
                # or we just need to retry them with a fresh browser session.
                err_msg = str(e).lower()
                if "invalid session id" in err_msg or "connection aborted" in err_msg or "connection refused" in err_msg or "no such window" in err_msg:
                    logger.warning("Browser session lost while processing %s. Will retry with a fresh browser session.", username)
                    print(f"  -> Browser session lost. Will recreate browser and retry {username}...")
                    # Recreate driver immediately
                    try:
                        self.driver.quit()
                    except Exception:
                        pass
                    self.driver = DriverFactory.create(self.config.browser)
                    # Do NOT write error status to file so it will be retried on next iteration or next run
                else:
                    logger.exception("Error processing user %s: %s", username, e)
                    print(f"  -> Error: {e}")
                    self._update_file_status(file_path, username, f"error:{str(e)[:50]}")

    def _update_file_status(self, file_path: Path, username: str, status: str) -> None:
        lines = []
        with file_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        
        new_lines = []
        updated = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                new_lines.append(line)
                continue
            parts = stripped.split(",")
            if parts[0].strip() == username:
                new_lines.append(f"{username},{status}\n")
                updated = True
            else:
                new_lines.append(line)
        
        if not updated:
            new_lines.append(f"{username},{status}\n")
            
        with file_path.open("w", encoding="utf-8") as f:
            f.writelines(new_lines)
