
import pathlib
from unittest.mock import MagicMock

from linter import run_linter

TEST_FOLDER = pathlib.Path(__file__).parent

def test_simple(monkeypatch):
    with (TEST_FOLDER / 'fixtures/empty.yaml').open('rb') as fd:
        issues = run_linter(fd)

    assert len(issues) == 1
    assert issues[0][1].startswith('Error during Swagger schema validation')


def test_helloworld(monkeypatch):
    with (TEST_FOLDER / 'fixtures/helloworld.yaml').open('rb') as fd:
        issues = run_linter(fd)

    assert issues == [('paths/"/greeting/{name}"', 'the POST method is used on a path ending with a path variable')]


def test_pet_store(monkeypatch):
    with (TEST_FOLDER / 'fixtures/pet-store.yaml').open('rb') as fd:
        issues = run_linter(fd)

    assert issues == []
