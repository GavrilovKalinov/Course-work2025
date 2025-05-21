#!/bin/bash
xhost +local:root
docker run \
	-e DISPLAY=$DISPLAY \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	-v ~/.Xauthority:/root/.Xauthority \
	-v ~/Downloads/torrents:/app/torrents \
	-v ~/Downloads/bittorrent:/app/downloads \
	course:latest
