from typing import Optional

from fastapi import Depends
from fastapi.params import Query

from api.v1.base import KirinRouter
from schemas.item import ItemInDBBase
from services.item import item_service


def hello_world(search_params: dict = None, *args, **kwargs):
    print("hello world", search_params.get("age"))
    # print(search_params["age"])
    search_params["age"] = "24"


def change_result(result: dict):
    # result["data"][0]["name"] = "changed name"
    # return result
    print(result)


async def filter_params(
        title: Optional[str] = Query(
            max_length=10000,
            default=None,
            description="filters params"
        ),
):
    return {k: v for k, v in locals().items() if v is not None}


router = KirinRouter(ItemInDBBase,
                     service=item_service,
                     # filters_dependencies=Depends(filter_params),
                     preprocess={"GET_ALL": [hello_world]},
                     postprocess={"GET_ALL": [change_result]})
