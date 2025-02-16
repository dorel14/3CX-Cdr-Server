FROM jpillora/dnsmasq


RUN mkdir /scripts

WORKDIR /scripts
COPY /dnsmasq/start.sh /scripts/start.sh


RUN chmod +x /scripts/start.sh

CMD ["/scripts/start.sh"]