#!/bin/bash
#
# originally contributed by @rbuffat to Toblerity/Fiona
set -e

########################################
# texlive
# https://www.tug.org/texlive/
#
# pandoc
# https://github.com/pandoc/dockerfiles#available-images
########################################
apt-get update
apt-get install -y texlive-full

# Test installation
echo "=========="
miktex --version
echo "=========="

# change back to travis build dir
cd $TRAVIS_BUILD_DIR
