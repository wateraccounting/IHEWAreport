#!/bin/bash
#
# originally contributed by @rbuffat to Toblerity/Fiona
set -e

########################################
# Miktex
# https://miktex.org/howto/install-miktex-unx
# https://hub.docker.com/r/miktex/miktex/dockerfile
#
# pandoc
# https://github.com/pandoc/dockerfiles#available-images
########################################
apt-get update
apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        dirmngr \
        ghostscript \
        gnupg \
        gosu \
        make \
        perl

apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys D6BC243565B2087BC3F897C9277A7293F59E4889

echo "deb http://miktex.org/download/ubuntu bionic universe" | tee /etc/apt/sources.list.d/miktex.list

apt-get update
apt-get install -y --no-install-recommends miktex

miktexsetup finish
initexmf --admin --set-config-value=[MPM]AutoInstall=1
#mpm --admin --update-db
#mpm --admin \
#    --install amsfonts \
#    --install biber-linux-x86_64
#initexmf --admin --update-fndb

export MIKTEX_USERCONFIG=/miktex/.miktex/texmfs/config
export MIKTEX_USERDATA=/miktex/.miktex/texmfs/data
export MIKTEX_USERINSTALL=/miktex/.miktex/texmfs/install

# Test installation
echo "=========="
miktex --version
echo "=========="

# change back to travis build dir
cd $TRAVIS_BUILD_DIR
