# LaTeX compiler service — canonical image for prod, local dev, and CI e2e.
#
# A fork of aslushnikov/latex-online (a self-hosted "compile a tar of .tex ->
# PDF" HTTP API) rebuilt on the TeX Live 2024 base so templates that use
# fontawesome5 (and other recent packages) compile. The upstream aslushnikov
# image is abandoned and ships TL2016 (missing fontawesome5); do NOT use it.
#
# The app source is baked in at build time (instant startup, no network needed
# at boot). Published to GHCR by .github/workflows/latex-image.yml whenever
# this directory changes; prod and CI pull that image instead of building.
FROM registry.gitlab.com/islandoftex/images/texlive:TL2024-historic
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates git-core nodejs npm \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/aslushnikov/latex-online /var/www \
 && cd /var/www \
 && npm ci
# An uploaded template using fontspec or unicode-math cannot compile under pdflatex
# at all, so xelatex is load-bearing once users bring their own LaTeX. The base image
# ships no xelatex.fmt: the engine generates it on first use, which costs ~8s and has
# been seen to fail outright with "I can't find the format file `xelatex.fmt'". That
# state lives in the container, so every recreated container pays and risks it again.
# Building it once here makes the engine's availability a property of the image.
RUN fmtutil-sys --byfmt xelatex
WORKDIR /var/www
ENV NODE_ENV=production
EXPOSE 2700
CMD ["node", "app.js"]
