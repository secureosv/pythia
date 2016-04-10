#!/bin/bash
cp examples-mkdocs.yml mkdocs.yml
mkdocs gh-deploy --clean
cp docs-mkdocs.yml mkdocs.yml
