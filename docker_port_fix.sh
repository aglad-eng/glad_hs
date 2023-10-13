#!/bin/bash

###
#  There are times that docker will glitch and continue
#  to consume ports, when it is no longer supposed to.
#  This occurs when its network database has networks that
#  no longer exist.  
#  This will fix that issue by deleting the current network db for docker
###

#stop all containers that are running
docker stop $(docker ps -aq)

#stop the docker daemon
sudo service docker stop

#clear network database for docker
sudo rm -f /var/lib/docker/network/files/local-kv.db

#restart the service
sudo service docker start