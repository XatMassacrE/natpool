FROM python:3.9
MAINTAINER natpool
ADD ./natpool.py /code/
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone
ENV LANG C.UTF-8
ENV PATH=$PATH:/usr/local/lib/python3.9/
ENV PYTHONPATH $PATH
WORKDIR /code
EXPOSE ${lport}
ENTRYPOINT [ "python", "-u","./natpool.py" ]