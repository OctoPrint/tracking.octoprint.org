#!/bin/bash

set -e

# nginx
NGINX_LOCATION_SOURCE=scripts/nginx/tracking.location.conf
NGINX_LOCATION_TARGET=/etc/nginx/snippets/tracking.location.conf
NGINX_LOG_SOURCE=scripts/nginx/logformat_tracking.conf
NGINX_LOG_TARGET=/etc/nginx/conf.d/logformat_tracking.conf

if cmp -s "$NGINX_LOCATION_SOURCE" "$NGINX_LOCATION_TARGET" && cmp -s "$NGINX_LOG_SOURCE" "$NGINX_LOG_TARGET"; then
        echo "Nginx config is unchanged"
else
        sudo cp -v "$NGINX_LOCATION_SOURCE" "$NGINX_LOCATION_TARGET" && sudo cp -v "$NGINX_LOG_SOURCE" "$NGINX_LOG_TARGET" && sudo nginx -t && sudo service nginx restart && echo "Deployed nginx config"
fi

# Logstash
LOGSTASH_CONFIG_SOURCE=scripts/logstash/logstash-tracking-live.conf
LOGSTASH_CONFIG_TARGET=/etc/logstash/conf.d/logstash-tracking-live.conf

if cmp -s "$LOGSTASH_CONFIG_SOURCE" "$LOGSTASH_CONFIG_TARGET"; then
        echo "Logstash config is unchanged"
else
        sudo cp -v "$LOGSTASH_CONFIG_SOURCE" "$LOGSTASH_CONFIG_TARGET" && sudo service logstash restart && echo "Deployed logstash config"
fi

# Curator
echo "Copying curator config"
sudo cp -v scripts/curator/*.yml /etc/curator/

echo "All done!"
