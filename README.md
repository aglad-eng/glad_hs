# glad_hs
A docker compose framework for a home server.  The first part of the read me is 
explanations on choices.  Skip to ["Setup"](https://github.com/aglad-eng/glad_hs#setup) 
to see instructions on how to set up and run the server.

Goals:  
  - Primary: To show an example set up of a basic home server.  Hopefully this 
  will allow others looking to set up some refferences on how I did mine.  
  - Secondary: To back up my current home server setup so that I can easily port 
  it to a new physical machine and only have to install docker, docker compose, 
  and adjust a few environment vairables to have a complete server environment set up.
      
**Note**:  This home server is designed around the idea that you want specific 
others (family members, friends etc) to access the server remotely and easily 
while preventing others from accessing it.  For that reason specific design 
decisions are made for ease of access.

**Warnings**:  This guide assumes that you are decently technical.  This means 
I won't explain everything in detail.  For example I won't be covering how to 
install docker as I assume you would be able to quickly google and found out 
how to install it properly.  Rather this repository is more of a skeletal 
framwork for a basic home server to get people started quickly, or to provide 
example configurations for common apps that, while I was creating my home server, 
had difficulty finding online.  

If you need more detail on some basics I have found the following guides helpful 
for many things:
  - https://www.smarthomebeginner.com/home-server/ 
  - https://www.smarthomebeginner.com/docker-media-server-2022/

## Essentials
  - Domain Name
  - Dynamic Domain Name System (DDNS)
  - SSL Certification
  - Reverse Proxy Application
  - Authentication Application
  - 
Something that you will need for a home server is a domain name and ddns 
provider.  The domain name will allow you to find your home server from outside 
your own network.  This is important when you attempting to set up a reverse 
proxy or a VPN.  Dynamic DNS (ddns) will update the domain registry with your 
current public IP address as your ISP changes you IP address.

## Domain Name and DDNS
### Free Domain Name
Many websites will give you a free domain name as long as it is a subdomain of 
their site.  I used Dynu.com for a free domain name.  They are easy to use and 
I found them to be the best for DDNS so it was simple to use them for the domain 
name as well.  If you want a specific domain name you can purchase a domain at 
many sites including google or dynu.  

### Free DDNS
Use Dynu.com for free ddns.  They were simple to set up, simple to edit, simple 
to use, support ddns with wild card certificates, and they will provide free 
ddns for up to 3 domains indefinetely.  If you find another provider than you 
enjoy I can add it here, but I found that most of the others had to be renewed 
after a month, have specific routers to work correctly, or did not support wild 
card certificates.  Dynu didn't have these issues and were great for my purpose.

### SSL Certification
Use acme.sh for the program that will certify things. The repository is 
https://github.com/acmesh-official/acme.sh. I changed its default Certificate 
authority (CA) to letsencrypt because acme.sh's standard CA is ZeroSSL.  Either 
is likely fine, but letsencrypt is currently very standard, free, and has a lot 
of QA support for newbies.  

When installed acme.sh will automatically create chron job to renew licenses.

to issue a wildcard certificat the format is 
`acme.sh  --issue -d <base domain>  -d '*.<base domain>'  --dns <dns_provider>`
Ex: `acme.sh  --issue -d my_domain.com  -d '*.my_domain.com'  --dns dns_dynu`

*Links:*
  - Change the CA: https://github.com/acmesh-official/acme.sh/wiki/Change-default-CA
  - DNS API: https://github.com/acmesh-official/acme.sh/wiki/dnsapi
  - DNS API for Dynu: https://github.com/acmesh-official/acme.sh/wiki/dnsapi#24-use-dynu-api

## Reverse Proxy Application

A reverse proxy allows you to access all your applications off of a single port. 
Web services normally use HTTPS which is standard on port 443.  However, only one
application per machine can be attached to a port.  So your reverse proxy will be
attached to the port.  Then based on the domain and path in the http request will 
redirect the http traffic to the correct application on your server.

### Nginx - Reason
I used Nginx for my reverse proxy.  It has been a big proxy manager and load 
balancer in the industry for a long time.  I often found the most common reason 
for not using it was because it was to complex and confusing for starters.  
However, I found it pretty simple after I found a decent tutorial.  

Nginx Proxy Manager and SWAG are other applications that you can use for reverse
proxies.  They both use Nginx on the backend.  I would suggest trying to use
the original Nginx when possible.  I find non-GUI configurations for servers
to work better long term and when you change hardware.  Additionally, the home use
programs like SWAG and Nginx Proxy Manager are not going to be as field tested 
as Nginx which is used by millions of people and businesses and I like my forward 
facing applications to be as robust and tested as possible.

### Nginx - Configuration
Nginx has a main configuration file called "nginx.conf".  In general you will 
want to leave this file alone.  It sets up some basic configuration for nginx 
and then tells nginx that each web server you want to hose will be defined in a 
subdirectory "conf.d".  The directory "conf.d" is normally organized to have a 
seperate file for each web server.  Nginx will parse the dirctory "conf.d" in 
alphabetical order and spin up each server defined in each file.  If you find a 
tutorial for the nginx configuration of a webserver/application that you want, 
but they are modifying the main nginx.conf simply create a new file in the 
"conf.d" directory and past the server{} code into the new file.

My nginx.conf has a single modification.  I create a variable called "internal" 
that maps internal IP addresses to it. This allows me to create different traffic 
routes for internal IPs compared to External IPs.  This breaks the "Zero trust" 
rule slightly, but it's done in a way to be overly cautious, not less cautious.

Each file in the conf.d directory is spun up in the order that they appear in 
the file structure (Alphebetically).  The first server that matches the incoming 
domain name will be used.  For that reason I prefix all of my server configuration 
files in conf.d with numbers.  This allows me to easily define the order that my 
webservers will be spun up in and the order that they will be matched in.  

Additionally I found that my webservers had a lot of duplicated code.  To reduce 
the duplication of code I created a "conf_templates" directory.  This directory 
holds default configurations for my webservers that are repeated.  For example 
the ssl.conf file holds the necessary lines to define my ssl certificates and my 
default ssl configuration.  Instead of having duplicate this code in every 
section I use it I use ``` include <filename>; ```  to include all of these 
settings into the necessary locations in each .conf file of my webservers.

## Authentication Application

I use an authentication program to put my applications that have no authentication
or whose authentication I do not trust.  This keeps my server secure while I am 
able to expose it to the internet.

### bitnami/oauth2-proxy - Reason
I used bitnami/oauth2-proxy as the image and google oauth2 as my authentication method.
  
I wanted to use Google Oauth 2.0.  I made this server to share with my family 
members, who are extremely not technical.  This allowed them to be able to sign 
into my webserver without having to create a new account or remember a new password.  
Additionally I felt that google oauth 2.0 would be well supported.  It also let 
me force 2 factor authentification on my family without having to make them set 
up a new account or athentication method.
  
If I were to choose another authentication method I would probably work with Authentik.

### bitnami/oauth2-proxy - Setup  
Setting everything up on googles side was decently simple.  I also found the 
settings for bitnami/oauth2-proxy simple.  I found issues trying to get it to 
connect to nginx.  My biggest issue was that there had been minor updates that 
made the nginx configuration change, but nearly all of the examples and tutorials 
I found were for the older configuration version.  Hopfully my configurations 
will serve as good examples and save others from the frustration I had setting 
it up.  Looking at the updated documentation for bitnami/oauth2-proxy as well as 
a [.conf](https://github.com/linuxserver/reverse-proxy-confs) file example 
provided by linuxserver for swag is how I figured out the changes in the configurations.

For the setup on googles end I found their 
[documentation](https://support.google.com/cloud/answer/6158849?hl=en) complete, 
but not helpful to begginers.  I found short youtube tutorials the best way to 
find out how to set up the oauth on googles side. 
 
# Setup
For proper setup you will first need to set up the essentials (domain name, 
ddns, ssl, oath2 configuration via google or another platform).  After having 
set up these steps you will need to create and edit necessary documents in the repository.
  
The necessary changes are explained below.  You can perform them manually or 
with the "setup.py" script.

## NGINX Setup
Each webserver I want has it's own .conf file in the conf.d/ directory.

**Steps:**
1. Copy and paste the nginx.conf file, the conf_templates directory, and the 
conf.d directory from nginx_config/examples into nginx_config/
1. Replace occurances of "my_domain.com" to the domain name that you have set 
up for your server. See: ["Free Domain Name"](https://github.com/aglad-eng/glad_hs#free-domain-name)
1. If you want to treat internal IP addresses and external IP addresses differently update the 
nginx.conf file at the "TODO" section.  You can see how I treat them differently
in the conf.d files for vaultwarden and immich.

**Note:**
These confs assume that the nginx container can reach other containers via 
their dns hostnames (defaults to container name) resolved via docker's internal 
dns. This is achieved through having the containers attached to the same user 
defined docker bridge network.  For security reasons I have each service on it's 
own network.  I create these networks using the "docker-network-all.sh" script.

### .ENV Setup
Docker compose will automatically look for a .env file in the same directory as 
the docker-compose.yml file specified.  It uses the .env file as local 
environment variables.  .env files are largely used for environment variables 
that you don't want public.  This often includes secrets such as passwords used 
by databases.  I have created a ".env.example" for each service that uses
a .env file.  You will need to copy it and rename it ".env".  Once the copy has 
been made and renamed edit each environment variable to their appropriate values.

### Oauth2 Setup
The oauth/ directory containes to examples files: oauth2_proxy.cfg.example and 
permitted_emails.txt.example.  Remove the .example from the end of the file names.  

Edit the necessary sections in oath2_proxy.cfg.  Each section that needs to 
changed will be marked with ``` ### CHANGE THIS ### ```.  

Replace the example email addresses with an the email addresses associated with 
the google accounts that you want to access your server in the 
permitted_emails.txt file.  Each email should be on it's own line as shown in 
the example.

### Filebrowser Setup
Filebrowser is a basic web ui for the file system of the server.  By default it 
uses a file as a binary dictionary.  For Filebrowser to start properly it needs 
an empty file to use as it's binary database.  Create an empty fb_data.db file 
under the fb_config/ directory.  The full path should be 
\<Path to repo\>/services/filebrowser/fb_data.db.  

### Running the services
Once everything has been set up start, you can start using your services.  You can
start seach service with `docker compose -f <path specific docker-compose.yml> up -d`.
Or if you want to start them all at the same time you can use the "docker-all.sh" 
script by using the command `docker-all.sh up`.  This script will recursevly find
every directory in "services/" and attempt to the command 
`docker compose -f ./services/<sub-directory>/docker-compose.yml up -d`.

# Useful sites and resources
  - General: https://www.smarthomebeginner.com/home-server/ 
  - General: https://www.smarthomebeginner.com/docker-media-server-2022/
  - Oauth2: https://oauth2-proxy.github.io/oauth2-proxy/docs/configuration/overview/
  - Oauth2: https://github.com/bitly/oauth2_proxy
  - Vaultwarden: https://github.com/dani-garcia/vaultwarden/blob/main/.env.template
  - VPN: https://github.com/kylemanna/docker-openvpn/blob/master/docs/docker-compose.md
  - SSL: https://github.com/acmesh-official/acme.sh
  - Nginx Examples: https://github.com/linuxserver/reverse-proxy-confs _(These 
  examples are for swag which uses nginx.  Swag is also a great tool for many of 
  the "essentials")._
  - Google oauth: https://support.google.com/cloud/answer/6158849?hl=en
