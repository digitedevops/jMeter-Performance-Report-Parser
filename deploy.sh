#!/bin/bash
export HOST_IP=10.0.2.250
cd /home/ubuntu/microservice
docker stop perfcompareservice || true && docker rm perfcompareservice || true
docker pull digite/ms-perfcompare:latest && docker rmi $(docker images -q -f dangling=true) && docker-compose up -d --remove-orphans