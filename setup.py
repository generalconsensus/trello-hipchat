from setuptools import setup, find_packages

setup(
    name="trello-hipchat",
    version = '0.1',
    maintainer='Luminoso Technologies, Inc.',
    maintainer_email='dev@luminoso.com',
    url = 'http://github.com/LuminosoInsight/trello-hipchat',
    platforms = ["any"],
    description = ("Integration between Trello and HipChat: send Trello "
                   "activity notifications to HipChat rooms"),
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'trello-hipchat = trello_hipchat.cli:main',
            ]},
)
