FROM liip/dnsmasq:1.0.0
#Permet de forcer le vidage de cahche des varaibles d'environnement
ARG CACHEBUST=1


COPY --chmod=755 /dnsmasq/start.sh /start.sh

RUN /start.sh

