FROM python:3.9.10

#ENV INPUT_FILE bla
#ENV BUFFER_FILE bla-bla


RUN apt-get -y update
RUN apt-get install -y libsndfile1
RUN apt-get install -y ffmpeg

RUN python3 -m venv /opt/venv

# Install dependencies:
COPY requirements.txt .
RUN /opt/venv/bin/pip install -r requirements.txt

# Run the application:
COPY network .
#CMD /opt/venv/bin/python main.py
#${INPUT_FILE} ${BUFFER_FILE}
CMD /opt/venv/bin/python server.py

EXPOSE 15000