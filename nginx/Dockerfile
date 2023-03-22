FROM nginx:1.15.8

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf
COPY project.conf /etc/nginx/conf.d/
COPY static /app/static

RUN mkdir /etc/nginx/ssl
RUN mkdir /etc/nginx/ssl/certs
RUN mkdir /etc/nginx/ssl/private


COPY www.sailorsdailyjill.social-ca.pem /etc/nginx/ssl/certs/www.sailorsdailyjill.social-ca.pem
COPY www.sailorsdailyjill.social.key /etc/nginx/ssl/private/www.sailorsdailyjill.social-ca.key
COPY www.sailorsdailyjill.social.crt /etc/nginx/ssl/certs/www.sailorsdailyjill.social.crt
COPY www.sailorsdailyjill.social-root.pem /etc/nginx/ssl/certs/www.sailorsdailyjill.social-root.pem