# Build stage
FROM nginx:1.17.10-alpine AS build

LABEL "com.datadoghq.ad.check_names"='["nginx"]'
LABEL "com.datadoghq.ad.init_configs"='[{}]'
LABEL "com.datadoghq.ad.instances"='[{"nginx_status_url": "http://%%host%%:81/nginx_status/"}]'
LABEL "com.datadoghq.ad.logs"='[{"source": "nginx", "service": "nginx", "log_processing_rules": [{"type": "multi_line", "name": "log_start_with_date", "pattern": "\\d{4}/\\d{2}/\\d{2}"}]}]'

COPY ./nginx/prod/ /etc/nginx/

RUN chown -R nginx:nginx /etc/nginx


# Production stage
FROM nginx:1.17.10-alpine

LABEL "com.datadoghq.ad.check_names"='["nginx"]'
LABEL "com.datadoghq.ad.init_configs"='[{}]'
LABEL "com.datadoghq.ad.instances"='[{"nginx_status_url": "http://%%host%%:81/nginx_status/"}]'
LABEL "com.datadoghq.ad.logs"='[{"source": "nginx", "service": "nginx", "log_processing_rules": [{"type": "multi_line", "name": "log_start_with_date", "pattern": "\\d{4}/\\d{2}/\\d{2}"}]}]'

COPY --chown=nginx:nginx --from=build /etc/nginx /etc/nginx

COPY --chown=nginx:nginx ./compose/production/nginx/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

ENTRYPOINT ["/entrypoint"]
CMD ["nginx", "-g", "daemon off;"]
