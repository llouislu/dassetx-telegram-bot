FROM python:3.8-slim-buster
COPY . /app
WORKDIR /app
RUN pip install --user -r requirements.txt
RUN pip install --user -r requirements-dev.txt
RUN python -m build
RUN pip install --user dist/*.whl
ENTRYPOINT ["python3", "-m", "dassetx_telegram_bot.main"]
