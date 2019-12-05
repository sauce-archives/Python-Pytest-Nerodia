import pytest

from simplesauce.options import SauceOptions
from simplesauce.session import SauceSession
from nerodia.browser import Browser

browsers = [
    'internet explorer',
    'safari',
    'edge',
    'chrome',
    'firefox'
]


@pytest.fixture(params=browsers)
def browser(request):
    opts = SauceOptions(request.param)
    opts.name = request.node.name
    session = SauceSession(options=opts)
    
    browser = Browser(browser=session.start())
    yield browser

    result = 'failed' if request.node.rep_call.failed else 'passed'
    session.update_test_result(result)
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
