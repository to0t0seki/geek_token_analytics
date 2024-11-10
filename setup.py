from setuptools import setup, find_packages

setup(
    name="geek_token_analytics",
    packages=find_packages(),
    version="0.1.0",
    install_requires=[
        "streamlit",
        "plotly",
        "pandas",
        "streamlit-aggrid",
        "cryptography"
    ],
    python_requires=">=3.8",
)