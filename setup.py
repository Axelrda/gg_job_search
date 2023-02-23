from setuptools import setup, find_packages

setup(
    name="gg_job_search",
    version="0.1",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "joblib"
    ],
    entry_points={
        "console_scripts": [
            "preprocess=preprocessing.preprocess:main"
        ]
    }
)
