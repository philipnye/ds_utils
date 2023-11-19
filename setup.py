import os
import setuptools
import shutil

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]


class CleanCommand(setuptools.Command):
    """
        Custom clean command to tidy up the project root.

        Notes:
            - Source: https://stackoverflow.com/a/3780822/4659442,
            https://sentry.io/answers/delete-a-file-or-folder-in-python/
    """
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if os.path.isdir("./utils.egg-info"):
            shutil.rmtree("./utils.egg-info")


setuptools.setup(
    name='utils',
    version="1.0.0",
    author="Philip Nye",
    author_email="philipnye@users.noreply.github.com",
    description="A collection of Python functions to solve common challenges.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/philipnye/utils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    cmdclass={
        'clean': CleanCommand,
    }
)
