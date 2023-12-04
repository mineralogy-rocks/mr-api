# Build stage
FROM nginx:1.17.10-alpine AS build

COPY ./nginx/prod/ /etc/nginx/

RUN chown -R nginx:nginx /etc/nginx


# Production stage
FROM nginx:1.17.10-alpine

LABEL "com.datadoghq.ad.check_names"='["nginx"]'
LABEL "com.datadoghq.ad.init_configs"='[{}]'
LABEL "com.datadoghq.ad.instances"='[{"nginx_status_url": "http://%%host%%:81/nginx_status/"}]'
LABEL "com.datadoghq.ad.logs"='[{"source":"nginx", "service":"nginx", "type": "file", "path": "/home/ubuntu/backend/nginx/_data/*.log"}]'

COPY --chown=nginx:nginx --from=build /etc/nginx /etc/nginx

COPY --chown=nginx:nginx ./compose/production/nginx/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

ENTRYPOINT ["/entrypoint"]
CMD ["nginx", "-g", "daemon off;"]
