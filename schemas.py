from pydantic import BaseModel, Field, AliasChoices

class Network(BaseModel):
    """
    Keeps information about network.
    """
    network: str = Field()
    isp: str = Field()
    ip: list[str] = Field(min_length=2,max_length=2)
    ip_int: list[int] = Field(validation_alias=AliasChoices('ip_int','int'),
                              min_length=2,max_length=2)

class NetworkList(BaseModel):
    """
    List from Network models
    """
    networks: list[Network | None] = Field()