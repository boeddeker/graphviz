"""pytest command line options and fixtures."""

import pytest

SKIP_EXE = '--skip-exe'


def pytest_addoption(parser):
    try:
        parser.addoption(SKIP_EXE, action='store_true',
                         help='Skip tests with pytest.mark.exe.'
                              ' Xfail tests with pytest.mark.exe(xfail=True).'
                              ' Skip doctests with doctest_mark_exe().'
                              ' Xfail doctests with doctest_mark_exe(xfail=True).'
                              ' exe marks tests requiring backend.DOT_BINARY.')
    except ValueError as e:  # pragma: no cover
        assert SKIP_EXE in str(e), f'fails because {SKIP_EXE!r} is already added'


def pytest_configure(config):
    config.addinivalue_line('markers',
                            f'exe(xfail): skip/xfail if {SKIP_EXE} is given')


def pytest_collection_modifyitems(config, items):
    if config.getoption(SKIP_EXE):
        for item in items:
            exe_marker = _make_exe_marker(item)
            if exe_marker is not None:
                item.add_marker(exe_marker)


def _make_exe_marker(item):
    def make_kwargs(**kwargs):
        return kwargs

    exe_values = [make_kwargs(*m.args, **m.kwargs)
                  for m in item.iter_markers(name='exe')]

    if exe_values:
        assert len(exe_values) == 1
        kwargs, = exe_values

        if kwargs.pop('xfail', None):
            kwargs.setdefault('reason', f'xfail by {SKIP_EXE} flag')
            return pytest.mark.xfail(**kwargs)
        else:
            kwargs.setdefault('reason', f'skipped by {SKIP_EXE} flag')
            return pytest.mark.skip(**kwargs)
    return None


@pytest.fixture(scope='session')
def platform():
    import platform
    return platform.system().lower()


@pytest.fixture(params=[False, True], ids=lambda q: f'quiet={q!r}')
def quiet(request):
    return request.param


@pytest.fixture
def sentinel(mocker):
    return mocker.sentinel


@pytest.fixture
def mock_render(mocker):
    yield mocker.patch('graphviz.backend.rendering.render', autospec=True)


@pytest.fixture
def mock_pipe(mocker):
    yield mocker.patch('graphviz.backend.piping.pipe', autospec=True)


@pytest.fixture
def mock_pipe_lines(mocker):
    yield mocker.patch('graphviz.backend.piping.pipe_lines', autospec=True)


@pytest.fixture
def mock_pipe_lines_string(mocker):
    yield mocker.patch('graphviz.backend.piping.pipe_lines_string', autospec=True)


@pytest.fixture
def mock_unflatten(mocker):
    yield mocker.patch('graphviz.backend.unflattening.unflatten', autospec=True)


@pytest.fixture(params=['darwin', 'freebsd', 'linux', 'windows'],
                ids=lambda p: f'platform={p!r}')
def mock_platform(monkeypatch, request):
    monkeypatch.setattr('graphviz.backend.viewing.PLATFORM', request.param)
    yield request.param


@pytest.fixture
def unknown_platform(monkeypatch, name='nonplatform'):
    monkeypatch.setattr('graphviz.backend.viewing.PLATFORM', name)
    yield name
