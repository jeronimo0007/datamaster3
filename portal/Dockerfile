FROM nginx:alpine
COPY portal/index.html portal/banca.html portal/roteiro.html portal/cola.html \
  portal/datamaster-00-visao-geral.png portal/datamaster-00-visao-geral.svg \
  portal/datamaster-03-mapa.png \
  portal/datamaster-01-batch-medallion.png portal/datamaster-01-batch-medallion.svg \
  portal/datamaster-02-online-gateway.png portal/datamaster-02-online-gateway.svg \
  /usr/share/nginx/html/
COPY portal/nginx.conf /etc/nginx/conf.d/default.conf
