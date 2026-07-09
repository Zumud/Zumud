# Local LaTeX compiler for development — mirrors the production image.
#
# Production runs a fork of aslushnikov/latex-online (a self-hosted "compile a tar of
# .tex -> PDF" HTTP API) rebuilt on the TeX Live 2024 base so templates that use
# fontawesome5 (and other recent packages) compile. The upstream aslushnikov image is
# abandoned and ships TL2016 (missing fontawesome5), so we do NOT use it.
#
# The app source isn't baked in: the entrypoint clones latex-online at startup and
# serves it on :2700 (same as prod). Build context only needs this file + the entrypoint.
FROM registry.gitlab.com/islandoftex/images/texlive:TL2024-historic
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates git-core nodejs npm \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
WORKDIR /
EXPOSE 2700
CMD ["/docker-entrypoint.sh"]
