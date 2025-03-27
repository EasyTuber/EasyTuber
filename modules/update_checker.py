import requests
import time
from packaging import version


class UpdateChecker:
    """
    Class responsible for checking available application updates on GitHub.

    This class periodically checks for new versions of the application by
    comparing the current version with the latest release on GitHub.

    Attributes:
        root: Main application instance
        config: Default application settings
        user_prefer: User preferences
        update_info (dict): Information about available update
        last_timestamp (float): Timestamp of last check
        update_interval_hours (int): Interval in hours between checks
        current_time (float): Current timestamp
    """

    def __init__(self, root):
        """
        Initialize the update checker.

        Args:
            root: Main application instance
        """
        self.root = root
        self.config = root.default_config
        self.user_prefer = root.user_prefer
        self.update_info = None
        self.last_timestamp = None
        self.update_interval_hours = 24
        self.current_time = time.time()

        self.get_last_update_check()

        if self.update_info and self.update_info["has_update"]:
            self.root.show_update_available(self.update_info)
            self.user_prefer.set("last_update_check", self.current_time)

    def get_last_update_check(self):
        """
        Checks when the last update check was performed and decides
        if it's necessary to check again based on the defined interval.
        """
        self.last_timestamp = self.user_prefer.get("last_update_check", 0)
        update_interval_seconds = self.update_interval_hours * 3600

        if self.current_time - self.last_timestamp >= update_interval_seconds:
            self.check_for_updates()

    def check_for_updates(self):
        """
        Checks for available updates by querying the GitHub API.

        Compares the current application version with the latest version available
        on GitHub and updates self.update_info with the result.
        """
        try:
            api_url = f"https://api.github.com/repos/{self.config.APP_REPO_OWNER}/{self.config.APP_REPO_NAME}/releases/latest"
            response = requests.get(api_url, timeout=10)  # Added timeout
            response.raise_for_status()

            latest_release = response.json()
            latest_version = latest_release["tag_name"].strip("v")

            if version.parse(latest_version) > version.parse(self.config.APP_VERSION):
                self.update_info = {
                    "has_update": True,
                    "latest_version": f"v{latest_version}",
                    "release_url": latest_release["html_url"],
                }
            else:
                self.update_info = {"has_update": False}

        except Exception as e:
            print(f"Error checking for updates: {e}")
            self.update_info = {"has_update": False}
