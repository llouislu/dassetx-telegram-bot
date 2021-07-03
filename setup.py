import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dassetx-telegram-bot",
    version="0.0.1",
    author="Louis Lu",
    author_email="louis.dev@outlook.com",
    description="This bot pushes price alerts on subscriptions for crypto currencies on Dassetx.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/llouislu/dassetx-telegram-bot",
    project_urls={
        "Bug Tracker": "https://github.com/llouislu/dassetx-telegram-bot/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "dassetx_telegram_bot"},
    packages=setuptools.find_packages(where="dassetx_telegram_bot"),
    python_requires=">=3.8",
)
