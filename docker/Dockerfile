FROM python:3.6
LABEL maintainer="Kang HJ kanghongjin@gmail.com"

WORKDIR /tmp
RUN apt-get update && apt-get install -y wget awscli
RUN mkdir /usr/local/bin/clingo
RUN curl -L https://github.com/potassco/clingo/releases/download/v5.2.2/clingo-5.2.2-linux-x86_64.tar.gz | tar -xz -C /usr/local/bin
ADD test.py /usr/local/bin/solve.py
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt


CMD ["python", "/usr/local/bin/solve.py"]