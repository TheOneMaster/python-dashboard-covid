FROM python:3

WORKDIR /app

COPY . .

RUN python3 -m pip install -U pandas dash plotly

CMD python -u ./main.py

EXPOSE 8000
