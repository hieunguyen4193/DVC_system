export MINIO_CONFIG_ENV_FILE=./minio.config
# export MINIO_CONFIG_ENV_FILE=./minio.config.mb
minio server --console-address :9411

# sudo lsof -i :5955
# sudo kill -9 PID

# MinIO Object Storage Server
# Copyright: 2015-2024 MinIO, Inc.
# License: GNU AGPLv3 - https://www.gnu.org/licenses/agpl-3.0.html
# Version: RELEASE.2024-07-04T14-25-45Z (go1.22.5 darwin/arm64)

# API: http://172.18.102.224:9000  http://127.0.0.1:9000 
#    RootUser: hieunguyen 
#    RootPass: genov4.cool 

# WebUI: http://172.18.102.224:9411 http://127.0.0.1:9411            
#    RootUser: hieunguyen 
#    RootPass: genov4.cool 

# CLI: https://min.io/docs/minio/linux/reference/minio-mc.html#quickstart
#    $ mc alias set 'myminio' 'http://172.18.102.224:9000' 'hieunguyen' 'genov4.cool'

# Docs: https://min.io/docs/minio/linux/index.html
# Status:         1 Online, 0 Offline. 
# STARTUP WARNINGS:
# - The standard parity is set to 0. This can lead to data loss.