# Contributin to Dcapy

We appretiate any contribution to the project. Here are 
detailed some specifications required to know if you would like to support 
this project by:

* Reporting Bugs
* Submit a fix
* proposing new features

## Main Repository with Github

We use Github to host the code and manage all relating task of a 
repository

If you would like to develop the project this guide should help to get 
started. 

## Get started

1. Fork the repository and create your branch from master

The dependencies manager and builder for Pypi is done through Poetry. The 
repo contains a `pyproject.toml` and `poetry.lock` files from which all 
dependencies can be easylly installed including the required to develop 
the project. Nonetheless a `requirements.txt` is also included.

2. If you've added code that should be tested, add tests. 

Most of the main classes declarations uses 
[Pydantic](https://pydantic-docs.helpmanual.io) which is a Data validation 
and settings management using python type annotations.    

3. If you've changed APIs, update the documentation.

The documentation page is managed by MkDocs which renders all the content of the `/docs` directory. It accepts Markdown files (.md) and thanks to the `mkdocs-jupyter` extension also Jupyter Notebooks (.ipynb). That way you could create jupyter notebooks examples and add it to the `docs/examples` folder. Every file included in the `/docs` directory that is intended to be shown in the Documentation page should be explicitly set up in the `./mkdocs.yml` file. 

4. Ensure the test passes.
5. Create the pull requestx

