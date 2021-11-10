FROM python:3

WORKDIR /app

COPY . .

RUN python3 -m pip install -U pandas==1.0.0 dash==1.14.0 plotly==4.9.0

CMD python -u ./main.py

EXPOSE 8000
