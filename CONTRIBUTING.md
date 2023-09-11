# Contributing

When contributing to this repository, please first discuss the change you wish to make via issue,
email, or any other method with the maintainers of this repository before making a change.

Please note we have a code of conduct, please follow it in all your interactions with the project.

## Contributing to the Codebase

The code is hosted on [GitHub](https://github.com/dlite-tools/github-deployments-dashboard),
so you will need to use [Git](http://git-scm.com/) to fork and clone the project,
and make changes to the codebase. Once you have obtained a copy of the code,
you should create a development environment that is separate from your existing
Python environment so that you can make and test changes without compromising your
own work environment.

### Creating a Python environment

To create an isolated development environment:

* Install [Poetry](https://python-poetry.org/)
* Make sure that you have cloned the repository
* Go to the project source directory
* Build environment. Run `poetry install`

### Run the test suite locally

Before submitting your changes for review, make sure to check that your changes
do not break any tests by running:

```shell
make tests
```

Do not forget to create new tests to cover the code alterations.

### Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the [README.md](README) with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
3. Increase the version numbers in any examples files and the [README.md](README) to the new version that this Pull Request would represent. The versioning scheme we use is [semantic versioning](http://semver.org/).
