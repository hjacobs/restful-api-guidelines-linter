#!/usr/bin/env python3

import re

import click
import yaml
from clickclick import error, warning
from swagger_spec_validator.validator20 import validate_spec


def compatibility_layer(spec):
    """Make specs compatible with older versions of Connexion."""
    if not isinstance(spec, dict):
        return spec

    # Make all response codes be string.
    # Most people use integers in YAML for status codes,
    # we don't want to annoy them by saying "response codes must be strings"
    for path_name, methods_available in spec.get('paths', {}).items():
        for method_name, method_def in methods_available.items():
            if (method_name == 'parameters' or not isinstance(
                    method_def, dict)):
                continue

            response_definitions = {}
            for response_code, response_def in method_def.get(
                    'responses', {}).items():
                response_definitions[str(response_code)] = response_def

            method_def['responses'] = response_definitions
    return spec


def lint_path_names(spec, resolver):
    """
    Must: Use lowercase separate words with hyphens for Path Segments

    http://zalando.github.io/restful-api-guidelines/naming/Naming.html#must-use-lowercase-separate-words-with-hyphens-for-path-segments
    """
    for path_name, methods_available in spec.get('paths', {}).items():
        if not re.match('^/[/a-z0-9{}.-]*$', path_name):
            yield 'paths/"{}"'.format(path_name)


def lint_http_methods(spec, resolver):
    """
    Must: Use HTTP Methods Correctly

    http://zalando.github.io/restful-api-guidelines/http/Http.html#must-use-http-methods-correctly
    """
    for path_name, methods_available in spec.get('paths', {}).items():
        # looks like a POST path ends with a path variable (probably ID..)
        if path_name.endswith('}') and 'post' in methods_available:
            yield 'paths/"{}"'.format(path_name), 'the POST method is used on a path ending with a path variable'


def lint_path_avoid_trailing_slashes(spec, resolver):
    """
    Must: Avoid Trailing Slashes
    """
    for path_name, methods_available in spec.get('paths', {}).items():
        if len(path_name) > 1 and path_name.endswith('/'):
            yield 'paths/"{}"'.format(path_name)


def lint_query_params(spec, resolver):
    """
    Must: Use snake_case (never camelCase) for Query Parameters

    http://zalando.github.io/restful-api-guidelines/naming/Naming.html#must-use-snakecase-never-camelcase-for-query-parameters
    """
    for path_name, methods_available in spec.get('paths', {}).items():
        for method_name, method_def in methods_available.items():
            if isinstance(method_def, dict):
                for param in method_def.get('parameters', {}):
                    if isinstance(param, dict) and '$ref' in param:
                        _, param = resolver.resolve(param.get('$ref'))
                    if param.get('type') == 'query':
                        if not re.match('^[a-z0-9_]*$', param.get('name', '')):
                            yield param


def lint_property_names(spec, resolver):
    """
    Must: Property names must be snake_case (and never camelCase).

    http://zalando.github.io/restful-api-guidelines/json-guidelines/JsonGuidelines.html#must-property-names-must-be-snakecase-and-never-camelcase
    """
    definitions = []
    for def_name, definition in spec.get('definitions', {}).items():
        if definition.get('type') == 'object':
            definitions.append((def_name, definition))

    while definitions:
        def_name, definition = definitions.pop()
        sub_props = definition.get('properties')
        if sub_props:
            for sub_prop_name in sub_props:
                if not re.match('^[a-z][a-z0-9_]*$', sub_prop_name):
                    yield 'definitions/{}/{}'.format(def_name, sub_prop_name)
                sub_prop = sub_props.get(sub_prop_name)
                sub_prop_type = sub_prop.get('type')
                if sub_prop_type == 'object':
                    definitions.append(('{}/{}'.format(def_name, sub_prop_name), sub_prop))



@click.command()
@click.argument('spec_file', type=click.File('rb'))
def cli(spec_file):
    spec = yaml.safe_load(spec_file)
    spec = compatibility_layer(spec)
    try:
        resolver = validate_spec(spec)
    except Exception as e:
        error('Error during Swagger schema validation:\n{}'.format(e))

    # collect all "rules" defined as functions starting with "lint_"
    rules = [f for name, f in globals().items() if name.startswith('lint_')]
    for func in rules:
        for issue in func(spec, resolver):
            if isinstance(issue, tuple):
                location, message = issue
            else:
                location = issue
                message = None
            warning('{}: {}{}'.format(location, message + ' ' if message else '', func.__doc__))


if __name__ == '__main__':
    cli()
