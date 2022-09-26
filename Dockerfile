FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV PYTHONPATH "${PYTHONPATH}:/"
ENV PORT=8000

COPY . /workdir

WORKDIR /workdir

# Install Poetry
RUN pip install poetry && \
    poetry config virtualenvs.create false


RUN poetry install --no-root --no-dev
ENTRYPOINT ["/workdir/entry.sh"]