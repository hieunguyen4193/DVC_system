# free the port before deploy new servers
# sudo lsof -i :5955
# sudo kill -9 PID

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker network rm elastic-net
export ELASTIC_PASSWORD="genov4" 
export KIBANA_PASSWORD="genov4.cool"

outputdir=/Users/hieunguyen/data/rds;

docker_local_dir=${outputdir}/elastic_savedir
MINIO_VOLUMES=${outputdir}/minio

mkdir -p $docker_local_dir
mkdir -p $MINIO_VOLUMES

docker network create elastic-net
docker run -p 127.0.0.1:9200:9200 -d --name elasticsearch --network elastic-net \
  -e ELASTIC_PASSWORD=$ELASTIC_PASSWORD \
  -e "discovery.type=single-node" \
  -e "xpack.security.http.ssl.enabled=false" \
  -e "xpack.license.self_generated.type=trial" \
  -v $docker_local_dir:/usr/share/elasticsearch/data \
  docker.elastic.co/elasticsearch/elasticsearch:8.14.2

sleep 30

# configure the Kibana password in the ES container
curl -u elastic:$ELASTIC_PASSWORD \
  -X POST \
  http://localhost:9200/_security/user/kibana_system/_password \
  -d '{"password":"'"$KIBANA_PASSWORD"'"}' \
  -H 'Content-Type: application/json'

docker run -p 127.0.0.1:5601:5601 -d --name kibana --network elastic-net \
  -e ELASTICSEARCH_URL=http://elasticsearch:9200 \
  -e ELASTICSEARCH_HOSTS=http://elasticsearch:9200 \
  -e ELASTICSEARCH_USERNAME=kibana_system \
  -e ELASTICSEARCH_PASSWORD=$KIBANA_PASSWORD \
  -e "xpack.security.enabled=false" \
  -e "xpack.license.self_generated.type=basic" \
  docker.elastic.co/kibana/kibana:8.14.2


##### launch minio sever
export MINIO_ROOT_USER=hieunguyen
export MINIO_ROOT_PASSWORD=genov4.cool
export MINIO_VOLUMES=$MINIO_VOLUMES
# export MINIO_VOLUMES="/media/hieunguyen/HD0/minio"
# export MINIO_VOLUMES="/Users/hieunguyen/src/data/minio"
# Start MinIO server
minio server --console-address :9412 --address :9411
