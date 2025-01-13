from setuptools import setup, find_packages

setup(
    name="southwest-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.26.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "scikit-learn>=0.24.2",
        "sqlalchemy>=1.4.23",
        "psycopg2-binary>=2.9.1",
        "python-dotenv>=0.19.0",
        "alembic>=1.7.0",
    ],
    python_requires=">=3.8",
) 