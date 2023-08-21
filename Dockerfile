FROM registry.talos.basic.ai/basicai/algorithm/images/framework/openpcdet:latest

# install aws cli and config
RUN pip install awscli \
    && mkdir -p ~/.aws \
    && printf "[default]\naws_access_key_id = ${BASICAI_ALGORITHM_AWS_ACCESS_KEY_READ}\naws_secret_access_key = ${BASICAI_ALGORITHM_AWS_ACCESS_SECRET_READ}\n" > ~/.aws/credentials

# install app
WORKDIR /app
COPY . ./
RUN pip install -e . \
    && rm -rf .cicd .gitlab-ci.yml

# download model file
RUN aws s3 cp ${MODEL_FILE_S3} ./

# start service
WORKDIR /app/pcdet_open
ENTRYPOINT ["python", "app.py", "../cbgs_voxel0075_centerpoint_nds_6648.pth"]
EXPOSE 5000

# sudo docker build -t registry.talos.basic.ai/basicai/algorithm/images/service/pcdet-open:latest .