# glad_hs
A docker-compose framework for a home server.

Goals:  
  - Primary: To show an example set up of a basic home server.  Hopefully this will allow others looking to set up some refferences on how I did mine.  
  - Secondary: To back up my current home server setup so that I can easily port it to a new physical machine and only have to install docker, docker compose, and adjust a few environment vairables to have a complete server environment set up.
      
Note:  This home server is designed around the idea that you want specific others (family members, friends etc) to access the server remotely and easily while preventing others from accessing it.  For that reason specific design decisions are made for ease of access.

Warnings:  This guide assumes that you are decently technical.  This means I won't explain everything in detail.  For example I won't be covering how to install docker as I assume you would be able to quickly google and found out how to install it properly.  Rather this repository is more of a skeletal framwork for a basic home server to get people started quickly, or to provide example configurations for common apps that, while I was creating my home server, had difficulty finding online.  

If you need more detail on some basics I have found the following guides helpful for many things:
  - https://www.smarthomebeginner.com/home-server/ 
  - https://www.smarthomebeginner.com/docker-media-server-2022/

### Essentials
  - Domain Name
  - Dynamic Domain Name System (DDNS)
  - SSL Certification
  - Reverse Proxy Application
  - Authentication Application
  - 
Something that you will need for a home server is a domain name and ddns provider.  The domain name will allow you to find your home server from outside your own network.  This is important when you attempting to set up a reverse proxy or a VPN.  Dynamic DNS will update the domain registry with your current public IP address as your ISP changes you IP address.

### Free Domain Name
Many websites will give you a free domain name as long as it is a subdomain of their site.  I used Dyanu.com for a free domain name.  They are easy to use and I found them to be the best for DDNS so it was simple to use them for the domain name as well.  If you want a specific domain name you can purchase a domain at many sites including google or dyanu.  

### Free DDNS
Use Dyanu.com for free ddns.  They were simple to set up, simple to edit, simple to use, support ddns with wild card certificates, and they will provide free ddns for up to 3 domains indefinetely.  If you find another provider than you enjoy I can add it here, but I found that most of the others had to be renewed after a month, have specific routers to work correctly, or did not support wild card certificates.  Dyanu didn't have these issues and were great for my purpose.

### SSL Certification
Use acme.sh for the program that will certify things. The repository is https://github.com/acmesh-official/acme.sh.
I changed its default CA to letsencrypt because its a standard CA is ZeroSSL.  Either is most likely fine, but letsencrypt is currently very standard, free, and has a lot of QA support for newbies.  

When installed acme.sh will automatically create chron job to renew licenses

to issue a wildcard certificat the format is "acme.sh  --issue -d <base domain>  -d '*.<base domain>'  --dns <dns_provider>"
Ex: "acme.sh  --issue -d my_domain.com  -d '*.my_domain.com'  --dns dns_dynu"

### Reverse Proxy Application
I used nginx for my reverse proxy.  It has been a big proxy manager and load balancer in the industry for a long time.  I often found the most common reason for not using it was because it was to complex and confusing for starters.  However, I found it pretty simple after I found a decent tutorial.  

Nginx has a main configuration file called "nginx.conf".  In general you will want to leave this file alone.  It sets up some basic configuration for nginx and then tells nginx that each web server you want to hose will be defined in a subdirectory "conf.d".  The directory "conf.d" is normally organized to have a seperate file for each web server.  Nginx will parse the dirctory "conf.d" in alphabetical order and spin up each server defined in each file.  If you find a tutorial for the nginx configuration of a webserver/application that you want, but they are modifying the main nginx.conf simply create a new file in the "conf.d" directory and past the server{} code into the new file.

I prefix all of my server configuration files in conf.d with numbers.  This allows me to easily define the order that my webservers will be spun up in.  

Additionally I found that my webservers had a lot of duplicated code.  To reduce the duplication of code I created a "conf_templates" directory.  This directory holds default configurations for my webservers that are repeated.  For example the ssl.conf file holds the necessary lines to define my ssl certificates and my default ssl configuration.  Instead of having duplicate this code in every section I use it I use "include <filename>;" to include all of these settings into the necessary locations in each .conf file of my webservers.

### Authentication Application
I used bitnami/oauth2-proxy as the image and google oauth2 as my authentication method.
  
I wanted to use Google Oauth 2.0.  I made this server to share with my family members, who are extremely not technical.  This allowed them to be able to sign into my webserver without having to create a new account or remember a new password.  Additionally I felt that google oauth 2.0 would be well supported.  It also let me force 2 factor authentification on my family without having to make them set up a new account or athentication method.
  
If I were to choose another authentication method I would probably work with Authelia.
  
Setting everything up on googles side was decently simple.  I also found the settings for bitnami/oauth2-proxy simple.  I found issues trying to get it to connect to nginx.  My biggest issue was that there had been minor updates that made the nginx configuration change, but nearly all of the examples and tutorials I found were for the older configuration version.  Hopfully my configurations will serve as good examples and save others from the frustration I had setting it up.
  
  
### Useful sites and resources
  - General: https://www.smarthomebeginner.com/home-server/ 
  - General: https://www.smarthomebeginner.com/docker-media-server-2022/
  - Oauth2: https://oauth2-proxy.github.io/oauth2-proxy/docs/configuration/overview/
  - Oauth2: https://github.com/bitly/oauth2_proxy
  - Vaultwarden: https://github.com/dani-garcia/vaultwarden/blob/main/.env.template
  - VPN: https://github.com/kylemanna/docker-openvpn/blob/master/docs/docker-compose.md
  - SSL: https://github.com/acmesh-official/acme.sh
