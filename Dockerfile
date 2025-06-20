FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN mkdir /vctk
# Aggiungi dataset VCTK (scarica manualmente o tramite script)
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
