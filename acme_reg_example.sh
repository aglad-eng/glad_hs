#!/bin/bash
###
# Step 1: Issue your wildcard certificate using DNS validation
#
# ** Make sure to replace the "dns_dynu" with whichever dns service you are using (I was using dynu.com). **
# See official acme.sh documentation for more details.
# https://github.com/acmesh-official/acme.sh/wiki/dnsapi
###
acme.sh --issue -d my_domain.com -d '*.my_domain.com' --dns dns_dynu --ecc

###
# Step 2: Install certificate and configure automatic nginx reload
# This copies the certificate to the location nginx expects and sets up automatic
# reload after each renewal, so nginx always uses the latest certificate
###
acme.sh --install-cert -d my_domain.com --ecc \
  --cert-file ~/certinfo/my_domain.com/cert.pem \
  --key-file ~/certinfo/my_domain.com/key.pem \
  --fullchain-file ~/certinfo/my_domain.com/fullchain.pem \
  --reloadcmd "docker exec nginx-glad_hs nginx -s reload"

###
# Optional: Force renewal (useful for testing)
###
# acme.sh --renew -d my_domain.com --force --ecc