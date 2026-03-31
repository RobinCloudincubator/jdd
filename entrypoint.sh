#!/bin/sh

if command -v php-fpm7 >/dev/null 2>&1; then
  php-fpm7
elif command -v php-fpm8.3 >/dev/null 2>&1; then
  php-fpm8.3
else
  php-fpm
fi
sleep 1
exec nginx -g "daemon off;"
