FROM nginx:1.17.10-alpine

COPY ./nginx/prod/ ./etc/nginx/

RUN chown -R nginx:nginx /etc/nginx

CMD ["/bin/sh", "-c", "envsubst '$${DOMAIN}' < /etc/nginx/conf.d/templates/domain.conf > /etc/nginx/conf.d/domain.conf && \
                       envsubst '$${DOMAIN}' < /etc/nginx/conf.d/templates/no-ssl.domain.conf > /etc/nginx/conf.d/no-ssl.domain.conf && \
                       envsubst '$${DOMAIN}' < /etc/nginx/h5bp/tls/templates/certificate_files.conf > /etc/nginx/h5bp/tls/certificate_files.conf && \
                       while :; do sleep 6h & wait $!; nginx -s reload; done & nginx -g 'daemon off;'"]
