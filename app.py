from fastapi import FastAPI

from schemas import NetworkList

app = FastAPI(title="Microservice for making list of networks", redoc_url=None)


@app.get("/networks", tags=['main'])
async def show_networks() -> NetworkList:
    with open("networks.json") as f:
        return NetworkList.model_validate_json(f.read())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, log_level=None, access_log=False)
