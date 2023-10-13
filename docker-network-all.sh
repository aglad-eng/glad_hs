#!/bin/bash

networks=( \
    "adguardhome_lan" \
    "filebrowser_lan" \
    "heimdall_lan" \
    "immich_lan"\
    "jellyfin_lan" \
    "nginx_lan" \
    "oauth_lan" \
    "openvpn_lan" \
    "vaultwarden_lan" )

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 [create|remove|list]"
  exit 1
fi

if [[ $1 == "create" ]]; then
  for network_name in "${networks[@]}"; do
    docker network create --driver bridge "$network_name"
    echo "Network '$network_name' created."
  done

elif [[ $1 == "remove" ]]; then
  for network_name in "${networks[@]}"; do
    docker network rm "$network_name"
    echo "Network '$network_name' removed."
  done

elif [[ $1 == "list" ]]; then
  echo "Available networks:"
  docker network ls

else
  echo "Invalid argument. Usage: $0 [create|remove|list]"
  exit 1
fi
