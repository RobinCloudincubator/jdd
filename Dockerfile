FROM ubuntu:latest

RUN apt-get -y update
RUN apt-get -y upgrade
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get install -y nginx php8.3-fpm
RUN sed -i 's|^listen = .*|listen = 127.0.0.1:9000|' /etc/php/8.3/fpm/pool.d/www.conf

WORKDIR /var/www/html
COPY . /var/www/html/

RUN mkdir -p /var/www/html/comparisons && chmod 777 /var/www/html/comparisons

COPY nginx.conf /etc/nginx/nginx.conf
RUN sed -i 's/^user nginx;/user www-data;/' /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
