import setuptools

setuptools.setup(
    name="opensearch_traffic_comparator",
    version="0.1",
    description="Tooling to help compare traffic streams from two clusters.",
    author="OpenSearch Migrations",
    py_modules=['traffic_comparator'],
    install_requires=[
        "Click",
        "deepdiff"
    ],
    extras_require={
        'dev': ['flake8', 'pytest']
    },
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'trafficcomparator = cli:cli'
        ]
    }
)
