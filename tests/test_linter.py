
import pathlib
from unittest.mock import MagicMock

from linter import run_linter

TEST_FOLDER = pathlib.Path(__file__).parent

def test_simple(monkeypatch):
    error = MagicMock()
    warning = MagicMock()
    monkeypatch.setattr('linter.error', error)
    monkeypatch.setattr('linter.warning', warning)
    with (TEST_FOLDER / 'fixtures/empty.yaml').open('rb') as fd:
        run_linter(fd)

    assert error.call_args[0][0].startswith('Error during Swagger schema validation')
    warning.assert_not_called()


def test_helloworld(monkeypatch):
    error = MagicMock()
    warning = MagicMock()
    monkeypatch.setattr('linter.error', error)
    monkeypatch.setattr('linter.warning', warning)
    with (TEST_FOLDER / 'fixtures/helloworld.yaml').open('rb') as fd:
        run_linter(fd)

    error.assert_not_called()
    assert 'the POST method is used on a path ending with a path variable' in warning.call_args[0][0]
