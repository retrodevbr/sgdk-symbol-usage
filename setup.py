from setuptools import setup

setup(
    name='sgdk-symbol-usage',
    version='1.0.0',
    py_modules=['generate_report'],
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'sgdk-symbol-usage=generate_report:main',
        ],
    },
    python_requires='>=3.6',
    author='retrodevbr',
    description='SGDK Symbol Usage Analyzer',
    url='https://github.com/retrodevbr/sgdk-symbol-usage',
)

