FROM traefik:v2.10
#Permet de forcer le vidage de cahche des varaibles d'environnement
ARG CACHEBUST=1
RUN mkdir /scripts
COPY /traefik/entrypoint.sh /scripts/entrypoint.sh
COPY /traefik/traefik.dynamic.toml.template /scripts/traefik.dynamic.toml.template
RUN chmod +x /scripts/entrypoint.sh