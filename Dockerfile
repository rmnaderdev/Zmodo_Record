FROM python:3 AS base
RUN mkdir -p /zmodo_output
RUN apt-get -y update
RUN apt-get install -y ffmpeg

FROM base as deps
RUN pip install psutil
RUN pip install requests

FROM deps as final
ADD zmodo-record.py /
CMD [ "python", "-u", "zmodo-record.py" ]