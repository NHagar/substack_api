import json
import os
from typing import Optional

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class SubstackAuth:
    """Handles authentication for Substack API requests."""

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        cookies_path: Optional[str] = None,
    ):
        """
        Initialize authentication handler.

        Parameters
        ----------
        email : str, optional
            Substack account email
        password : str, optional
            Substack account password
        cookies_path : str, optional
            Path to save/load session cookies
        """
        self.email = email
        self.password = password
        self.cookies_path = cookies_path or os.path.expanduser(
            "~/.substack_cookies.json"
        )
        self.session = requests.Session()
        self.authenticated = False

        # Set default headers
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        # Try to load existing cookies
        if os.path.exists(self.cookies_path):
            self.load_cookies()
        elif email and password:
            self.login()

    def login(self) -> bool:
        """
        Login to Substack using Selenium WebDriver.

        Returns
        -------
        bool
            True if login successful, False otherwise
        """
        if not self.email or not self.password:
            raise ValueError("Email and password required for login")

        print(f"Logging in as {self.email}...")

        # Setup Chrome options for headless mode
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.get("https://substack.com/sign-in")

            # Wait for login form
            wait = WebDriverWait(driver, 10)

            # Enter email
            email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_input.send_keys(self.email)

            # Click Sign in with password
            sign_in_button = driver.find_element(
                By.XPATH, "//a[contains(text(), 'Sign in with password')]"
            )
            sign_in_button.click()

            # Wait for password field
            password_input = wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_input.send_keys(self.password)

            # Submit login
            login_button = driver.find_element(
                By.XPATH, "//button[contains(text(), 'Continue')]"
            )
            login_button.click()

            # Wait for redirect after successful login
            wait.until(lambda d: d.current_url != "https://substack.com/sign-in")

            # Extract cookies
            cookies = driver.get_cookies()

            # Convert to requests session cookies
            for cookie in cookies:
                self.session.cookies.set(
                    cookie["name"],
                    cookie["value"],
                    domain=cookie.get("domain"),
                    path=cookie.get("path", "/"),
                )

            # Save cookies
            self.save_cookies()
            self.authenticated = True
            print("Login successful!")
            return True

        except TimeoutException:
            print("Login failed: Timeout waiting for elements")
            return False
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
        finally:
            if driver:
                driver.quit()

    def save_cookies(self) -> None:
        """Save session cookies to file."""
        cookies = {}
        for cookie in self.session.cookies:
            cookies[cookie.name] = {
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "secure": cookie.secure,
                "expires": cookie.expires,
            }

        with open(self.cookies_path, "w") as f:
            json.dump(cookies, f)

    def load_cookies(self) -> bool:
        """
        Load cookies from file.

        Returns
        -------
        bool
            True if cookies loaded successfully
        """
        try:
            with open(self.cookies_path, "r") as f:
                cookies = json.load(f)

            for name, cookie in cookies.items():
                self.session.cookies.set(
                    name,
                    cookie["value"],
                    domain=cookie.get("domain"),
                    path=cookie.get("path", "/"),
                    secure=cookie.get("secure", False),
                )

            return True

        except Exception as e:
            print(f"Failed to load cookies: {str(e)}")
            return False

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Make authenticated GET request.

        Parameters
        ----------
        url : str
            URL to request
        **kwargs
            Additional arguments to pass to requests.get

        Returns
        -------
        requests.Response
            Response object
        """
        return self.session.get(url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """
        Make authenticated POST request.

        Parameters
        ----------
        url : str
            URL to request
        **kwargs
            Additional arguments to pass to requests.post

        Returns
        -------
        requests.Response
            Response object
        """
        return self.session.post(url, **kwargs)
