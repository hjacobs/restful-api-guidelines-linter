#!/usr/bin/env python3

import collections
import re
import sys

import click
import inflect
import yaml
from clickclick import warning, info
from swagger_spec_validator.validator20 import validate_spec

Issue = collections.namedtuple('Issue', 'location message guideline')


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


def lint_base_path(spec, resolver):
    """
    Must: Do Not Use URI Versioning

    https://zalando.github.io/restful-api-guidelines/compatibility/Compatibility.html#must-do-not-use-uri-versioning
    """
    base_path = spec.get('basePath', '')
    if re.match('.*v[0-9].*', base_path):
        yield 'basePath'


def lint_path_names(spec, resolver):
    """
    Must: Use lowercase separate words with hyphens for Path Segments

    http://zalando.github.io/restful-api-guidelines/naming/Naming.html#must-use-lowercase-separate-words-with-hyphens-for-path-segments
    """
    for path_name, methods_available in spec.get('paths', {}).items():
        path_name_without_variables = re.sub('{[^}]*}', '', path_name)
        if not re.match('^/[/a-z0-9.-]*$', path_name_without_variables):
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

    https://zalando.github.io/restful-api-guidelines/naming/Naming.html#must-avoid-trailing-slashes
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
        for sub_prop_name, sub_prop in definition.get('properties', {}).items():
            if not re.match('^[a-z][a-z0-9_]*$', sub_prop_name):
                yield 'definitions/{}/{}'.format(def_name, sub_prop_name)
            sub_prop_type = sub_prop.get('type')
            if sub_prop_type == 'object':
                definitions.append(('{}/{}'.format(def_name, sub_prop_name), sub_prop))


def lint_response_objects(spec, resolver):
    """
    Must: Always Return JSON Objects As Top-Level Data Structures To Support Extensibility

    https://zalando.github.io/restful-api-guidelines/compatibility/Compatibility.html#must-always-return-json-objects-as-toplevel-data-structures-to-support-extensibility
    """

    for path_name, methods_available in spec.get('paths', {}).items():
        for method_name, method_def in methods_available.items():
            if isinstance(method_def, dict):
                for status_code, response_def in method_def.get('responses', {}).items():
                    schema_type = response_def.get('schema', {}).get('type')
                    if schema_type and schema_type != 'object':
                        yield 'paths/"{}"/{}/responses/{}'.format(path_name, method_name, status_code)


def lint_plural_resource_names(spec, resolver):
    """
    Must: Pluralize Resource Names

    https://zalando.github.io/restful-api-guidelines/naming/Naming.html#must-pluralize-resource-names
    """
    inflect_engine = inflect.engine()
    for path_name, methods_available in spec.get('paths', {}).items():
        path_name_without_variables = re.sub('{[^}]*}', '', path_name)
        for segment in path_name_without_variables.split('/'):
            if segment != '.well-known':
                resource = ' '.join(segment.split('-'))
                if resource:
                    singular = inflect_engine.singular_noun(resource)
                    plural = inflect_engine.plural_noun(resource)
                    if singular == resource or (not singular and plural and plural != resource):
                        yield 'paths/"{}"'.format(path_name), '"{}" is not in plural form'.format(resource)


def run_linter(spec_file, verbose: bool=False):
    spec = yaml.safe_load(spec_file)
    spec = compatibility_layer(spec)
    if verbose:
        info('Validating OpenAPI spec..')
    try:
        resolver = validate_spec(spec)
    except Exception as e:
        msg = 'Error during Swagger schema validation:\n{}'.format(e)
        return [Issue(location='', message=msg, guideline='Must: Provide API Reference Definition using OpenAPI')]

    # collect all "rules" defined as functions starting with "lint_"
    rules = [f for name, f in globals().items() if name.startswith('lint_')]
    issues = []
    for func in rules:
        if verbose:
            info('Linting {}..'.format(func.__name__.split('_', 1)[-1]))
        for issue in func(spec, resolver):
            if isinstance(issue, tuple):
                location, message = issue
            else:
                location = issue
                message = None
            issues.append(Issue(location=location, message=message or '', guideline=func.__doc__))
    return sorted(issues)


@click.command()
@click.argument('spec_file', type=click.File('rb'))
@click.option('-v', '--verbose', is_flag=True)
def cli(spec_file, verbose: bool):
    issues = run_linter(spec_file, verbose)
    for issue in issues:
        warning('{}: {}{}'.format(issue.location, issue.message, issue.guideline))
    sys.exit(len(issues))


def main():
    cli()
