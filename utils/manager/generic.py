from typing import Literal, Protocol, TypeVar
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc, func, inspect, select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.selectable import Select
import exceptions
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from pydantic import BaseModel


Model = TypeVar("Model")


class GenericManager:
    author_field_name: str = "created_by"

    def ___init__(self, model: Model, verbose_name: str | None):
        self.model = model
        self.verbose_name = verbose_name or self.model.__name__

    def _select(self, fields: list[str] = ["*"], load: list[str] = []) -> Select:
        """
        Generate a SQLAlchemy SELECT query for retrieving data from the database.

        Args:
            fields (list[str]): A set of field names to select.
            load (list[str]): A set of related fields to eagerly load using selectinload.

        Returns:
            sqlalchemy.sql.selectable.Select: A SQLAlchemy SELECT query.
        """

        # Only retrieve fields needed
        if "*" not in fields:
            f = [getattr(self.model, field) for field in fields]
            query = select(*f)
        else:
            query = select(self.model)

        # For retrive related fields
        for field in load:
            query = query.options(selectinload(getattr(self.model, field)))

        return query

    def _filter(self, query: Select, **kwargs) -> Select:
        """
        Filter a SQLAlchemy query based on specified conditions.

        Args:
            query (sqlalchemy.sql.selectable.Select): The SQLAlchemy query to filter.
            **kwargs: Keyword arguments representing filtering conditions.
                Use `key__in` for `IN` clauses, e.g., `field__in=[value1, value2]`.

        Returns:
            sqlalchemy.sql.selectable.Select: The filtered SQLAlchemy query.
        """
        for key, value in kwargs.items():
            if key.endswith("__in"):
                query = query.filter(
                    getattr(self.model, key.replace("__in", "")).in_(value)
                )
            else:
                query = query.where(getattr(self.model, key) == value)

        return query

    def _paginate(self, query: Select, page: int = 1, limit: int = 100) -> Select:
        """
        Paginate a SQLAlchemy query.

        Args:
            query (sqlalchemy.sql.selectable.Select): The SQLAlchemy query to paginate.
            page (int): The page number to retrieve (1-based).
            limit (int): The maximum number of results per page.

        Returns:
            sqlalchemy.sql.selectable.Select: The paginated SQLAlchemy query.
        """
        skip = (page - 1) * limit
        return query.offset(skip).limit(limit)

    def _order_by(
        self, query: Select, fields: str | list[str], mode: str = "desc"
    ) -> Select:
        """
        Modify an SQLAlchemy query to include sorting by one or more fields in ascending or descending order.

        Args:
            query (Select): The SQLAlchemy Select query to be modified.
            fields (Union[str, List[str]]): The field(s) by which to sort.
            mode (str): The sorting mode, either "asc" (ascending) or "desc" (descending).

        Returns:
            Select: The modified SQLAlchemy Select query with sorting applied.

        Raises:
            ValueError: If an invalid sorting mode is provided or a field does not exist.
        """
        if mode not in ["asc", "desc"]:
            raise ValueError("Invalid sorting mode. Choose 'asc' or 'desc'.")

        fields = [fields] if isinstance(fields, str) else fields

        for field in fields:
            if not hasattr(self.model, field):
                raise ValueError(f"Field '{field}' does not exist in the model.")
            order_func = desc if mode == "desc" else asc
            query = query.order_by(order_func(getattr(self.model, field)))

        return query

    async def _get_all_scalars(
        self, db: AsyncSession, query: Select | None = None
    ) -> list[Model]:
        """
        Retrieve a list of instances from the database.

        Args:
            db (AsyncSession): The asynchronous database session.
            query (sqlalchemy.sql.selectable.Select): The SQLAlchemy query to execute.

        Returns:
            list[Model]: A list of instances retrieved from the database.
        """
        query = self.select() if query is None else query
        response = await db.scalars(query)
        result = response.all()

        return result

    async def _get_scalar(
        self, db: AsyncSession, query: Select, raise_error: bool = False
    ) -> Model | None:
        """
        Retrieve a single instance from the database based on the provided SQLAlchemy query.

        Args:
            db (AsyncSession): The asynchronous database session.
            query (sqlalchemy.sql.selectable.Select): The SQLAlchemy query to execute.
            raise_error (bool, optional): If True, raise a NoResultFound exception if no instance is found. Default is False.

        Returns:
            Type[BaseModel]: The retrieved instance from the database or None if not found.
        Raises:
            NoResultFound: If `raise_error` is True and no instance is found.
        """
        response = await db.execute(query)
        instance = response.scalars().first()

        if raise_error is True and instance is None:
            raise exceptions.NotFound

        return instance

    def _handle_db_errors(self, error: IntegrityError):
        if isinstance(error.orig.__cause__, UniqueViolationError):
            raise exceptions.AlreadyExists
        if isinstance(error.orig.__cause__, ForeignKeyViolationError):
            raise exceptions.NoReference
        raise

    async def save(
        self,
        db: AsyncSession,
        instance: Model,
        load: list[str] = [],
        action: Literal["commit", "flush"] = "commit",
    ) -> Model | None:
        """
        Save or flush changes to the database and handle exceptions gracefully.
        """
        try:
            await (db.flush() if action == "flush" else db.commit())
            if instance:
                await db.refresh(instance, attribute_names=list(load))
            return instance
        except IntegrityError as error:
            await db.rollback()
            self._handle_db_errors(error)

    def _reset(self):
        """
        Reset the query state.
        """
        self._db = None
        self._query = None

    def query(
        self,
        db: AsyncSession,
        select: list[str] = ["*"],
        load: list[str] = [],
        **kwargs,
    ) -> Model:
        """
        Initialize query construction with specified fields, load relationships, and filters.
        """
        self._db = db
        self._query = self._filter(self._select(select, load), **kwargs)
        return self

    def paginate(self, page: int = 1, limit: int = 100) -> Model:
        """
        Apply pagination to the query.
        """
        if self._query is not None:
            self._query = self._paginate(self._query, page=page, limit=limit)
        return self

    def order_by(self, fields: str | list[str], mode: str = "desc") -> Model:
        """
        Apply ordering to the query.
        """
        if self._query is not None:
            self._query = self._order_by(self._query, fields, mode)
        return self

    async def one(self, raise_error: bool = True) -> Model:
        """
        Execute the query and return a single result.
        """
        if self._db is not None and self._query is not None:
            result = await self._get_scalar(
                self._db, self._query, raise_error=raise_error
            )
            self._reset()
            return result
        return None

    async def all(self) -> list[Model]:
        """
        Execute the query and return all results.
        """
        if self._db is not None and self._query is not None:
            result = await self._get_all_scalars(self._db, self._query)
            self._reset()
            return result
        return []

    async def create(
        self,
        db: AsyncSession,
        schema: BaseModel | None = None,
        load: list[str] = [],
        exclude: list[str] = [],
        user: UUID | None = None,
        action: Literal["commit", "flush"] = "commit",
        save: bool = True,
    ) -> Model:
        """
        Creates and persists a new instance of the model in the database.

        This method initializes a new model instance using either the provided Pydantic schema or a default constructor.

        Args:
            db (AsyncSession): The asynchronous database session to use for database operations.
            schema (BaseModel | None): A Pydantic schema representing the data for creating the instance. 
            load (list[str]): A list of relationship attributes to load eagerly. Defaults to an empty list.
            exclude (list[str]): A list of fields to exclude when creating the instance from the schema.
            user (UUID | None): The UUID of the user who is creating this instance, used for setting the 'created_by' field.
            action (Literal["commit", "flush"]): Specifies whether to immediately 'commit' the transaction or 'flush' for deferred commit.
            save (bool): Indicates whether to save the instance to the database immediately. Defaults to True.

        Returns:
            Model: The newly created model instance, which is either persisted or pending persistence based on the 'save' argument.

        Raises:
            AlreadyExist: Raised if an instance with conflicting unique constraints is found in the database.
            NoReference: Raised if a foreign key constraint violation occurs.
            Exception: Raised for any other exceptions encountered during the database operation.
        """

        if schema:
            instance = self.model(
                **schema.model_dump(exclude_unset=True, exclude=exclude)
            )
        else:
            instance = self.model()

        # Saving author
        if user and hasattr(instance, self.author_field_name):
            setattr(instance, self.author_field_name, user)

        # Adding new instance to db transaction
        db.add(instance)

        # Saving or not
        return await self.save(db, instance, load, action) if save else instance

    async def update(
        self,
        db: AsyncSession,
        instance: Model,
        schema: BaseModel,
        load: list[str] = [],
        exclude: list[str] = [],
        action: Literal["commit", "flush"] = "commit",
        save: bool = True,
    ) -> Model:
        """
        Updates an existing instance in the database with new data provided through a Pydantic schema.

        This method applies updates to an existing model instance using data from the provided Pydantic schema.

        Args:
            db (AsyncSession): The asynchronous database session used for executing the update operation.
            instance (Model): The existing model instance in the database to be updated.
            schema (BaseModel): A Pydantic schema containing the data to be used for updating the instance. 
                                The schema should reflect the structure of the model being updated.
            load (list[str]): A list of relationship attributes of the instance to load eagerly.
            exclude (list[str]): A list of fields to be excluded from the update operation.
            action (Literal["commit", "flush"]): Specifies the database transaction action to take after the update. 
            save (bool): Determines whether to save the changes to the database immediately.

        Returns:
            Model: The updated model instance, reflecting the changes made. 
                   The instance is either immediately persisted or pending persistence based on the 'save' argument.

        Raises:
            Exception: Any exceptions raised during the update operation are propagated for handling by the caller.
        """

        for field, value in schema.model_dump(
            exclude_unset=True, exclude=exclude
        ).items():
            setattr(instance, field, value)

        # Saving or not
        return await self.save(db, instance, load, action) if save else instance


    async def delete(
        self,
        db: AsyncSession,
        instance: Model,
        action: Literal["commit", "flush"] = "commit",
    ) -> Model:
        """
        Delete an existing database instance.

        Args:
            db (AsyncSession): The asynchronous database session.
            instance (Model): The database instance to be deleted.

        Returns:
            Type[BaseModel]: The deleted instance.

        Raises:
            Exception: Any exceptions raised during the database deletion operation.
        """
        await db.delete(instance)
        await self.save(db, instance, action=action)
        return instance