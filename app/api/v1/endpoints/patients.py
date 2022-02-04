from typing import Optional

from fastapi import Depends
from fastapi.params import Query

from api.deps import get_current_active_user, get_current_active_superuser
from api.v1.base import KirinRouter
from schemas.patient import PatientInDBBase
from services.patient import patient_service


def hello_world(search_params: dict = None, *args, **kwargs):
    print("hello world", search_params.get("age"))
    # print(search_params["age"])
    search_params["age"] = "24"


def change_result(result: dict):
    result["data"][0]["name"] = "changed name"
    # return result
    print(result)


async def filter_params(
        skip: Optional[int] = 0,
        limit: Optional[int] = 100,
        name: Optional[str] = Query(
            max_length=10000,
            default=None,
            description="filters params"
        ),
        age: Optional[str] = Query(
            max_length=10000,
            default=None,
            description="filters params"
        )
):
    return {k: v for k, v in locals().items() if v is not None}


router = KirinRouter(PatientInDBBase,
                     service=patient_service,
                     filters_dependencies=Depends(filter_params),
                     get_all_dependencies=[Depends(get_current_active_superuser)],
                     preprocess={"GET_ALL": [hello_world]},
                     postprocess={"GET_ALL": [change_result]})
