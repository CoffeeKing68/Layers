from pytest import fixture

def pytest_addoption(parser):
    parser.addoption('--save-images', action='store_true',
            help='Save images generated by tests')

@fixture()
def save_images(pytestconfig):
    return pytestconfig.getoption("save_images")

# def pytest_generate_tests(metafunc):
#     option_value = metafunc.config.option.save_images
#     if 'save-images' in metafunc.fixturenames and option_value is not None:
#         metafunc.parametrize("name", [option_value])
