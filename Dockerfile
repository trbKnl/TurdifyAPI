FROM arm32v7/python:buster

# qemu
COPY qemu-arm-static /usr/bin/

# FROM python:latest

# Install cmake to make dlib
RUN apt-get update && apt-get -y install cmake

# Install python packages
# The COPY of requirements,txt is separated from the "main" copy 
# To prevent rebuilding the cache, if another file, not requirements.txt,
# changes.
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy the main app
COPY . /app

EXPOSE 8888

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8888"]
