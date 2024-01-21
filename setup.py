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
        if os.path.isdir("./ds_utils.egg-info"):
            shutil.rmtree("./ds_utils.egg-info")


setuptools.setup(
    name='ds_utils',
    version="2.0.2",
    author="Philip Nye",
    author_email="philipnye@users.noreply.github.com",
    description="A collection of Python functions to execute common data science operations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/philipnye/ds_utils",
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
