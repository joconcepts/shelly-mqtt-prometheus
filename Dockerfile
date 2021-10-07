FROM python:alpine
RUN pip install paho-mqtt prometheus-client
COPY main.py /
CMD ["python", "-u", "main.py"]
