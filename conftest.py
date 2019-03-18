import pytest
from _pytest.runner import runtestprotocol
from nerodia.browser import Browser
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import RemoteConnection
from os import environ


single_browser = [{
    "seleniumVersion": '3.4.0',
    "platform": "Windows 10",
    "browserName": "firefox",
    "version": "60.0"
}]

browsers = [
    {
        "seleniumVersion": '3.4.0',
        "platform": "Windows 10",
        "browserName": "MicrosoftEdge",
        "version": "14.14393"
    }, {
        "seleniumVersion": '3.4.0',
        "platform": "Windows 10",
        "browserName": "firefox",
        "version": "60.0"
    }, {
        "seleniumVersion": '3.4.0',
        "platform": "Windows 7",
        "browserName": "internet explorer",
        "version": "11.0"
    }, {
        "seleniumVersion": '3.4.0',
        "platform": "OS X 10.12",
        "browserName": "safari",
        "version": "11.0"
    }, {
        "seleniumVersion": '3.4.0',
        "platform": "OS X 10.11",
        "browserName": "chrome",
        "version": "69.0",
        "extendedDebugging": True
    }]

def pytest_generate_tests(metafunc):
    if 'browser' in metafunc.fixturenames:
        metafunc.parametrize('browser_config',
                             browsers,
                             ids=_generate_param_ids('broswerConfig', browsers),
                             scope='function')

def _generate_param_ids(name, values):
    return [("<%s:%s>" % (name, value)).replace('.', '_') for value in values]

@pytest.fixture
def browser(request, browser_config):
    caps = {}
    caps.update(browser_config)

    build_tag = "nerodia-build"
    username = environ.get('SAUCE_USERNAME', None)
    access_key = environ.get('SAUCE_ACCESS_KEY', None)

    selenium_endpoint = "http://ondemand.saucelabs.com/wd/hub"
    
    caps['username'] = username
    caps['accesskey'] = access_key
    caps['name'] = request.node.name
    caps['build'] = build_tag

    executor = RemoteConnection(selenium_endpoint, resolve_ip=False)
    remote = webdriver.Remote(
        command_executor=executor,
        desired_capabilities=caps
    )

    browser = Browser(browser=remote, desired_capabilities=caps)
    yield browser
    
    sauce_result = "failed" if request.node.rep_call.failed else "passed"
    browser.execute_script("sauce:job-result={}".format(sauce_result))
    browser.quit()

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Needed pytest hook for accessing pass/fail results
    in the pytest fixture here.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    return rep