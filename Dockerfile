FROM python:3.8-alpine

ENV TOKEN=1111
ENV ACCESS=1111:2222
ENV TRANSMISSION_URL=localhost
ENV TRANSMISSION_LOGIN=admin
ENV TRANSMISSION_PASSWORD=1234
ENV TRANSMISSION_PORT=9091
ENV TIME_SHEDULE_SEC=10
ENV SOCKS5_LOGIN=admin
ENV SOCKS5_PASSWORD=4321
ENV SOCKS5_ADDRESS=localhost

WORKDIR /transmission_telegram

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /transmission_telegram/

ENTRYPOINT ["python", "bot.py", "&"]
CMD ["python", "shedule.py", "&"]

EXPOSE 443