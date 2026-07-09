#!/bin/bash
set -e

# Clone and install latex-online (the compile API), then serve it on :2700.
# Mirrors the production entrypoint so the local compiler behaves identically.
rm -rf /var/www
git clone https://github.com/aslushnikov/latex-online /var/www
cd /var/www
npm ci .

export NODE_ENV=production
export VERSION=$(git rev-parse HEAD)

npm install -g forever
forever --killTree app.js
