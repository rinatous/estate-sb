#!/usr/bin/env bash
THISDIR=$(dirname $(readlink -f $0))
cd $THISDIR
/usr/bin/pip3 install -r webapp.pkgs
