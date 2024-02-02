from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from app import schemas
from app.crud import crud
from project.database import get_async_session
from utils.manager import exceptions

router = APIRouter(tags=["v1"])


@router.get("/examples")
async def get_examples(
    page: Annotated[int, Query(gt=0)] = 1,
    limit: Annotated[int, Query(gt=0, le=50)] = 10,
    db: AsyncSession = Depends(get_async_session),
) -> list[schemas.Example]:
    return await crud.Example.query(db).paginate(page, limit).all()


@router.get("/examples/{example_id:int}")
async def get_one_example(
    example_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> schemas.Example:
    try:
        return await crud.Example.query(db, id=example_id).one()
    except exceptions.NotFound as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail)


@router.post("/examples")
async def create_example(
    schema: schemas.ExampleCreate,
    db: AsyncSession = Depends(get_async_session),
) -> schemas.Example:
    return await crud.Example.create(db, schema)


@router.put("/examples/{example_id:int}")
async def update_device(
    example_id: int,
    schema: schemas.ExampleUpdate,
    db: AsyncSession = Depends(get_async_session),
) -> schemas.Example:
    try:
        instance = await crud.Example.query(db, id=example_id).one()
        return await crud.Example.update(db, instance=instance, schema=schema)
    except exceptions.NotFound as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail)


@router.delete("/examples/{example_id:int}")
async def delete_example(
    example_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> schemas.Example:
    try:
        instance = await crud.Example.query(db, id=example_id).one()
        return await crud.Example.delete(db, instance)
    except exceptions.NotFound as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail)
