FROM public.ecr.aws/docker/library/python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /project

COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

RUN ["chmod", "+x", "startup.sh"]

CMD ["/bin/bash","-c","./startup.sh"]
