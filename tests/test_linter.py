
import pathlib
from unittest.mock import MagicMock

from linter import Issue, run_linter

TEST_FOLDER = pathlib.Path(__file__).parent

def test_simple(monkeypatch):
    with (TEST_FOLDER / 'fixtures/empty.yaml').open('rb') as fd:
        issues = run_linter(fd)

    assert len(issues) == 1
    assert issues[0].message.startswith('Error during Swagger schema validation')


def test_helloworld(monkeypatch):
    with (TEST_FOLDER / 'fixtures/helloworld.yaml').open('rb') as fd:
        issues = run_linter(fd)

    assert len(issues) == 4
    assert issues[0].guideline.strip().startswith('Must: Do Not Use URI Versioning')
    assert issues[1].message == '"greeting" is not in plural form'
    assert issues[2].message == 'the POST method is used on a path ending with a path variable'
    assert issues[3].location == 'paths/"/greeting/{name}"/post/responses/200'


def test_pet_store(monkeypatch):
    with (TEST_FOLDER / 'fixtures/pet-store.yaml').open('rb') as fd:
        issues = run_linter(fd)

    assert len(issues) == 1
    assert issues[0].location == 'paths/"/pets"/get/responses/200'
