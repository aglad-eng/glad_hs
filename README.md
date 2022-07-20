# glad_hs
A docker-compose framework for a home server


### freeddns
Use Dyanu.com for free ddns.

### Certification for SSL
Use acme.sh for the program that will certify things. The repository is https://github.com/acmesh-official/acme.sh.
I changed its default CA to letsencrypt because its a standard CA is ZeroSSL.

When installed it will automatically create chron job to renew licenses

to issue a wildcard certificat the format is "acme.sh  --issue -d <base domain>  -d '*.<base domain>'  --dns <dns_provider>"
Ex: "acme.sh  --issue -d my_domain.com  -d '*.my_domain.com'  --dns dns_dynu"