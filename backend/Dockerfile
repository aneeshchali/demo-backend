FROM python:alpine
# setup environment variable
ENV DockerHOME=/home/app/backend

# set work directory
RUN mkdir -p $DockerHOME

# where your code lives
WORKDIR $DockerHOME

# set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip

# copy whole project to your docker home directory.
COPY requirements.txt $DockerHOME
# run this command to install all dependencies
RUN \
     apk add --no-cache postgresql-libs && \
      apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
     python3 -m pip install --no-cache-dir -r requirements.txt && \
    apk --purge del .build-deps


# port where the Django app runs
COPY . $DockerHOME

#EXPOSE 8000
## start server

CMD ["python" ,"manage.py", "makemigrations"]
CMD ["python" ,"manage.py", "migrate"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]