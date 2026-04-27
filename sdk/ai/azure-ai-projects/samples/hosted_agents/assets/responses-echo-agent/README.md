# Responses Echo Agent

## Push to Azure Container Registry

Before building the image, uncomment the code in `main.py`.

Build the image:
```bash
docker build -t <your-acr-name>.azurecr.io/<repository-name>/<image-name>:latest .
```

Login to Azure Container Registry:
```bash
az acr login --name <your-acr-name>
```

Push the image:
```bash
docker push <your-acr-name>.azurecr.io/<repository-name>/<image-name>:latest
```
