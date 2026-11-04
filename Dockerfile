FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code and data are mounted as a volume by build.sh
CMD ["python", "build.py"]
