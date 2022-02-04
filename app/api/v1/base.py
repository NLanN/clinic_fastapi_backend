import json
from typing import Generic, Type, TypeVar, Optional, Any, Callable, List, Sequence, Dict, Union

from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.types import DecoratedCallable
from pydantic import BaseModel
from pydantic.utils import NoneType
from sqlalchemy.orm import Session
from starlette.requests import Request

from db.deps import get_session
from db.mixin import DBMixin

T = TypeVar("T", bound=BaseModel)
DEPENDENCIES = Optional[Sequence[Depends]]


class KirinRouter(Generic[T], APIRouter):
    def __init__(self, schema: Type[T],
                 prefix: Optional[str] = "",
                 *,
                 session_func: Optional[Session] = None,
                 preprocess: Dict[str, List[Callable]] = {},
                 postprocess: Dict[str, List[Callable]] = {},
                 filters_dependencies: Union[NoneType, DEPENDENCIES] = None,
                 authenticate_dependencies: Union[NoneType, DEPENDENCIES] = None,
                 get_all_dependencies: Union[bool, DEPENDENCIES] = True,
                 get_one_dependencies: Union[bool, DEPENDENCIES] = True,
                 post_one_dependencies: Union[bool, DEPENDENCIES] = True,
                 put_one_dependencies: Union[bool, DEPENDENCIES] = True,
                 delete_all_dependencies: Union[bool, DEPENDENCIES] = True,
                 delete_one_dependencies: Union[bool, DEPENDENCIES] = True,
                 service: Type[DBMixin],
                 **kwargs: Any,
                 ):
        self.authenticate_dependencies = authenticate_dependencies
        self.prefix: str = prefix
        self.schema: Type[T] = schema
        self.get_session = session_func or get_session
        self.service: Type[DBMixin] = service
        self.exclude_methods: Optional[List[str]] = None
        self.filters_dependencies = filters_dependencies
        self.get_all_dependencies = get_all_dependencies
        self.get_one_dependencies = get_one_dependencies
        self.post_one_dependencies = post_one_dependencies
        self.put_one_dependencies = put_one_dependencies
        self.delete_all_dependencies = delete_all_dependencies
        self.delete_one_dependencies = delete_one_dependencies
        self.preprocess = preprocess
        self.postprocess = postprocess

        class GetAllModel(BaseModel):
            count: Optional[int] = 0
            data: Optional[List[self.schema]] = []  # type: ignore

        GetAllModel.__name__ = f"GetAllModel<{self.schema.__name__}>"

        super().__init__(prefix=self.prefix, **kwargs)
        if self.get_all_dependencies:
            self._add_api_route(
                "/",
                self._get_all(),
                methods=["GET"],
                response_model=GetAllModel,  # type: ignore
                summary="Get All",
                dependencies=self.get_all_dependencies,
            )
        if self.get_one_dependencies:
            self._add_api_route(
                "/{id}",
                self._get_one(),
                methods=["GET"],
                response_model=Optional[self.schema],  # type: ignore
                summary="Get One",
                dependencies=self.get_one_dependencies
            )
        if self.post_one_dependencies:
            self._add_api_route(
                "/",
                self._create_one(),
                methods=["POST"],
                response_model=Optional[self.schema],  # type: ignore
                summary="POST One",
                dependencies=post_one_dependencies
            )
        if self.put_one_dependencies:
            self._add_api_route(
                "/{id}",
                self._update_one(),
                methods=["PUT"],
                response_model=Optional[self.schema],  # type: ignore
                summary="PUT One",
                dependencies=put_one_dependencies
            )
        if self.delete_all_dependencies:
            self._add_api_route(
                "/",
                self._delete_all(),
                methods=["DELETE"],
                response_model=Optional[self.schema],  # type: ignore
                summary="DELETE All",
                dependencies=delete_all_dependencies
            )
        if self.delete_one_dependencies:
            self._add_api_route(
                "/",
                self._delete_all(),
                methods=["DELETE"],
                response_model=Optional[self.schema],  # type: ignore
                summary="DELETE All",
                dependencies=delete_all_dependencies
            )

    def _add_api_route(
            self,
            path: str,
            endpoint: Callable[..., Any],
            dependencies: Union[bool, DEPENDENCIES],
            error_responses: Optional[List[HTTPException]] = None,
            **kwargs: Any,
    ) -> None:
        dependencies = [] if isinstance(dependencies, bool) else dependencies
        responses: Any = (
            {err.status_code: {"detail": err.detail} for err in error_responses}
            if error_responses
            else None
        )

        super().add_api_route(
            path, endpoint, responses=responses, dependencies=dependencies, **kwargs
        )

    def _default_filters_dependencies(self,
                                      skip: Optional[int] = 0,
                                      limit: Optional[int] = 100, ):
        return {k: v for k, v in locals().items() if v is not None}

    def _default_authenticate_dependencies(self
                                           ):
        return None

    def _get_all(self):
        def route(session: Session = Depends(self.get_session),
                  filters: Optional[Any] = self.filters_dependencies or Depends(self._default_filters_dependencies),
                  authenticated: Optional[Any] = self.authenticate_dependencies or Depends(
                      self._default_authenticate_dependencies),
                  request: Request = None):
            list_preprocess = self.preprocess.get("GET_ALL", None)
            search_params = request.query_params._dict
            skip = filters.get("skip")
            limit = filters.get("limit")

            if list_preprocess:
                for pre in list_preprocess:
                    pre(search_params)
                filters = search_params.get("filters")
                skip = search_params.get("skip")
                limit = search_params.get("limit")

            if isinstance(filters, str):
                filters = json.loads(filters)
            if filters:
                count, results = self.service.get_all_with_filter_and_paginate(
                    session=session, skip=skip, limit=limit, flt=filters)
            else:
                count, results = self.service.get_all_with_paginate(
                    session=session, skip=skip, limit=limit, flt=filters)
            results = jsonable_encoder(results)
            results = {"count": count, "data": results}
            self._post_process("GET_ALL", results)
            return results

        return route

    def _get_one(self, *args: Any, **kwargs: Any):
        def route(id=id, session: Session = Depends(self.get_session)):
            results = self.service.get(session=session, id=id)
            return self._post_process_by_id("GET_ONE", results, instance_id=id)

        return route

    def _create_one(self):
        def route(model: self.schema,  # type: ignore
                  session: Session = Depends(self.get_session),
                  ):
            results = self.service.create(session=session, obj_in=model)
            return self._post_process("POST_ONE", results)

        return route

    def _update_one(self):
        def route(model: self.schema,  # type: ignore
                  id=id,  # type: ignore    # noqa: F821
                  session: Session = Depends(self.get_session),
                  ):
            results = self.service.find_and_update(session=session, id=id, obj_in=model)
            if not results:
                raise HTTPException(400, detail="This record does not exist")
            return self._post_process_by_id("PUT_ONE", results, instance_id=id)

        return route

    def _delete_one(self):
        def route(id=id,
                  session: Session = Depends(self.get_session),
                  ):
            results = self.service.remove(session=session, id=id)
            if not results:
                raise HTTPException(400, detail="This record does not exist")

            return self._post_process_by_id("DELETE_ONE", results, instance_id=id)

        return route

    def _delete_all(self):
        def route(session: Session = Depends(self.get_session),
                  ):
            results = self.service.remove_all(session=session)
            if not results:
                raise HTTPException(400, detail="Unknown Error")
            return JSONResponse(status_code=200, content={"detail": "Delete all records successfully"})

        return route

    def _post_process(self, pros_type: str, results: Any):
        list_postprocess = self.postprocess.get(pros_type, None)
        if list_postprocess:
            for postprocess in list_postprocess:
                postprocess(results)
        return results

    def _post_process_by_id(self, pros_type: str, results: Any, instance_id: Any = None):
        list_postprocess = self.postprocess.get(pros_type, None)
        if list_postprocess:
            for postprocess in list_postprocess:
                results = postprocess(instance_id, results)
        return results

    def api_route(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """Overrides and exiting route if it exists"""
        methods = kwargs["methods"] if "methods" in kwargs else ["GET"]
        self.remove_api_route(path, methods)
        return super().api_route(path, *args, **kwargs)

    def get(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["Get"])
        return super().get(path, *args, **kwargs)

    def post(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["POST"])
        return super().post(path, *args, **kwargs)

    def put(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["PUT"])
        return super().put(path, *args, **kwargs)

    def delete(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["DELETE"])
        return super().delete(path, *args, **kwargs)

    def remove_api_route(self, path: str, methods: List[str]) -> None:
        methods_ = set(methods)

        for route in self.routes:
            if (
                    route.path == f"{self.prefix}{path}"  # type: ignore
                    and route.methods == methods_  # type: ignore
            ):
                self.routes.remove(route)
