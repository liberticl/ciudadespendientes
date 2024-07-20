echo "Eliminando todo lo que tiene docker"
docker container prune
docker images -f "dangling=true"
docker rmi $(docker images -q)

echo "Levantando el docker de Ciudades Pendientes"
docker-compose up -d