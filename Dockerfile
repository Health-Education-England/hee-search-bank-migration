# set base image
FROM rappdw/docker-java-python:zulu1.8.0_262-python3.7.9

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# command to run on container start
CMD [ "python", "/scripts/main.py" ]