FROM nginx:latest
RUN rm /etc/nginx/conf.d/default.conf
RUN mkdir /static
COPY ./sites-enabled /etc/nginx/conf.d
COPY ./ssl /etc/nginx/ssl

