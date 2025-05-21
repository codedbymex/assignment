import pytest
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService

def pytest_addoption(parser):
    parser.addoption(
        "--headed", action="store_true", default=False,
        help="Run browsers in headed (non-headless) mode"
    )


@pytest.fixture(scope="session")
def config():
    with open("test_config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(params=["chrome", "firefox"], scope="function")
def driver(request, config):
    browser = request.param
    headed = request.config.getoption("--headed")
    window_size = config["browser"].get("window_size", [1280, 800])
    implicit_wait = config["browser"].get("implicitly_wait", 5)

    if browser == "chrome":
        options = ChromeOptions()
        if not headed:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
        drv = webdriver.Chrome(options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        options.headless = not headed
        service = FirefoxService(GeckoDriverManager().install())

        drv = webdriver.Firefox(options=options, service=service)
        drv.set_window_size(*window_size)

    else:
        raise ValueError(f"Unsupported browser: {browser}")

    drv.implicitly_wait(implicit_wait)
    yield drv
    drv.quit()
