from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from project.database import get_async_session
from app import schemas
from app.crud import crud


router = APIRouter()


@router.get("/examples")
async def get_examples(
    page: Annotated[int, Query(gt=0)] = 1,
    limit: Annotated[int, Query(gt=0, le=5000)] = 10,
    db: AsyncSession = Depends(get_async_session),
) -> list[schemas.Example]:
    return await crud.Example.query(db).paginate(page, limit).all()


@router.post("/examples")
async def create_example(
    schema: schemas.ExampleCreate,
    db: AsyncSession = Depends(get_async_session),
) -> schemas.Example:
    return await crud.Example.create(db, schema)


@router.put("/examples/{example_id:int}")
async def update_device(
    example_id: int,
    schema: schemas.DeviceUpdate,
    db: AsyncSession = Depends(get_async_session),
) -> schemas.Example:
    instance = await crud.Example.query(db, id=example_id).one()
    return await crud.Example.update(db, instance=instance, schema=schema)


@router.delete("/examples/{example_id:int}")
async def delete_example(
    example_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> schemas.Example:
    instance = await crud.Example.fetch_query(db, id=example_id).one()
    return await crud.Example.delete(db, instance)
