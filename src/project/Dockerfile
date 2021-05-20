FROM python:3.7-buster
#FROM arm32v6/python:3.7-buster

RUN adduser --system --home /home/instrument --shell /bin/sh --uid 1001 --group instrument\
    && pip install --upgrade pip\
    && pip install pyserial PyYAML coloredlogs numpy scipy opcua\
    && sed -i -e /dialout/s/$/,instrument/ /etc/group

USER instrument
RUN mkdir -p /home/instrument/python
COPY --chown=instrument:instrument ./src/ /home/instrument/python/.
WORKDIR /home/instrument/python

#CMD ["/bin/sh", "-c", "sleep 1000000000"]
ENTRYPOINT ["python", "-m", "project.ismatec_deltav"]
