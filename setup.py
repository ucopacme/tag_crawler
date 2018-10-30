from setuptools import setup

setup(
    name="tag_crawler",
    version='0.0.1',
    py_modules=['tag_crawler'],
    install_requires=[
        'Click',
        'boto3',
        'organizer',
    ],
    entry_points='''
        [console_scripts]
        tag_crawler=tag_crawler:cli
    ''',
)
