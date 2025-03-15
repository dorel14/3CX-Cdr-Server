FROM traefik:v2.10
ARG CACHEBUST=1
WORKDIR /scripts
COPY /traefik/entrypoint.sh entrypoint.sh
COPY /traefik/traefik.dynamic.toml.template traefik.dynamic.toml.template
RUN chmod +x entrypoint.sh