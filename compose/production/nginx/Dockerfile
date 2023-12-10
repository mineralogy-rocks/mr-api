# Build stage
FROM nginx:1.17.10-alpine AS build

COPY ./nginx/prod/ /etc/nginx/

RUN chown -R nginx:nginx /etc/nginx


# Production stage
FROM nginx:1.17.10-alpine

ENV DD_SERVICE="nginx"
ENV DD_ENV="production"
ENV DD_VERSION="0.1.0"
ENV DD_APPSEC_ENABLED=true
ENV DD_LOGS_INJECTION=true

LABEL "com.datadoghq.tags.service"="nginx"
LABEL "com.datadoghq.tags.env"="production"

COPY --chown=nginx:nginx --from=build /etc/nginx /etc/nginx

COPY --chown=nginx:nginx ./compose/production/nginx/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

ENTRYPOINT ["/entrypoint"]
CMD ["nginx", "-g", "daemon off;"]
