#!/usr/bin/env python3

import linter

supported_guidelines = set()
for name, func in linter.__dict__.items():
    if name.startswith('lint_'):
        lines = [line.strip() for line in func.__doc__.strip().split('\n') if line.strip()]
        supported_guidelines.add((lines[0], ''.join(lines[1:])))

with open('README.rst', 'r') as fd:
    old_contents = fd.read()

new_lines = []
done = False
for line in old_contents.split('\n'):
    if line.startswith('*'):
        if not done:
            for guideline in sorted(supported_guidelines):
                new_lines.append('* `{} <{}>`_'.format(guideline[0], guideline[1]))
            done = True
    else:
        new_lines.append(line)

with open('README.rst', 'w') as fd:
    fd.write('\n'.join(new_lines))
