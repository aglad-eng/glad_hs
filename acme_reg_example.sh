#!/bin/bash

###
#  This will register your main domain
##
acme.sh  --issue  --standalone  -d 'my_domain.com'

###
#  This will register your wild card certificate.  
#
#  ** Make sure to replace the "dns_dynu" with which ever dns service you are using (I was using dynu.com). **
#  See official acme.sh documentation for more details.
#  https://github.com/acmesh-official/acme.sh/wiki/dnsapi
acme.sh  --issue -d *.my_domain.com  -d '*.my_domain.com'  --dns dns_dynu