FROM python:3.8-slim

#ADD ./ ./
COPY . .

RUN apt-get update \
&& apt-get install build-essential -y \
&& apt-get clean 


RUN pip3 install -r requirements.txt

EXPOSE 3500

CMD ["python3","-u","api.py"]