# -*- coding: utf-8 -*-

"""
AWS S3 only support list_objects API but not server side filtering.
Normally, we have to call the list_object api and use IF ELSE statement to
filter S3 object. However, list_objects API might be expensive and time consuming
if we have many S3 object.

This module allows you to only call list_objects API once and cache everything
in a SQLite database. Then you can use SQL to filter S3 object. Also, you can
reload the database to get the latest data when necessary.

This is similar to S3 inventory feature, however, it is more free and more flexible.

Requirements::

    s3pathlib>=2.1.2,<3.0.0
    sqlalchemy>-2.0.0,<3.0.0

Usage:

.. code-block:: python

    import sqlalchemy as sa
    from aws_s3_search import create_sqlite_engine, S3Object, S3Database

    # create an in-memory sqlite engine
    engine = create_sqlite_engine(path=None)

    # create database
    s3db = S3Database(
        engine=engine,
        expire=900, # the cache will expire after 900 seconds
        s3dir_uri_list=[
            "s3://my-bucket/", # scan all objects in the bucket
        ],
    )

    s3db.load_all()

    # print loaded s3 dir list
    print(self.db.loaded_s3dir_list()) == 0

    # print loaded s3 object list
    print(self.db.s3object_list()) == 0

    stmt = sa.select(S3Object).where(
        S3Object.size >= 1000000, # size >= 1MB
        S3Object.tags["key"].as_string() == "value", # has tag {"key": "value"}
    )
"""

import typing as T
import hashlib
import dataclasses
from datetime import datetime, timedelta

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects import sqlite
from s3pathlib import S3Path
from func_args import NOTHING


if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client


def get_md5(s: str) -> str:
    """
    Get the md5 hash of a string.
    """
    m = hashlib.md5()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


def create_sqlite_engine(
    driver: T.Optional[str] = None,
    path: T.Optional[str] = None,
) -> sa.engine:
    """
    Create a sqlite engine for sqlalchemy.

    :param driver: See https://docs.sqlalchemy.org/en/latest/core/engines.html#sqlite.
    :param path: the path to the sqlite database file. If None, use in-memory database.
    """
    if driver is None:
        driver = "sqlite"
    if path is None:
        path = ":memory:"
    return sa.create_engine(f"{driver}:///{path}")


class Base(orm.DeclarativeBase):
    pass


class S3Object(Base):
    """
    The s3_objects database table schema.

    If the s3 object is s3://my-bucket/folder/file.txt, and it's loaded s3dir
    is s3://my-bucket/, then

    :param uri: "s3://my-bucket/folder/file.txt"
    :param s3dir_md5: md5 of "s3://my-bucket/"
    :param bucket: "my-bucket"
    :param key: "folder/file.txt"
    :param dirpath: "/folder"
    :param dirname: "folder"
    :param basename: "file.txt"
    :param fname: "file"
    :param ext: ".txt"
    :param obj_update_at: object last_update_time
    :param etag: object etag
    :param size: object size in bytes
    :param meta: metadata as dictionary, if not available, then use {}
    :param tags: tags as dictionary, if not available, then use {}
    :param update_time: the time when the s3 object information is loaded into
        the search database
    :param expire_time: the time when this record should be considered as "expired"
    """

    __tablename__ = "s3_objects"

    uri: orm.Mapped[str] = orm.mapped_column(sa.String, primary_key=True)
    s3dir_md5: orm.Mapped[str] = orm.mapped_column(sa.String)
    bucket: orm.Mapped[str] = orm.mapped_column(sa.String)
    key: orm.Mapped[str] = orm.mapped_column(sa.String)
    dirpath: orm.Mapped[str] = orm.mapped_column(sa.String)
    dirname: orm.Mapped[str] = orm.mapped_column(sa.String)
    basename: orm.Mapped[str] = orm.mapped_column(sa.String)
    fname: orm.Mapped[str] = orm.mapped_column(sa.String)
    ext: orm.Mapped[str] = orm.mapped_column(sa.String)
    obj_update_at: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime, index=True)
    etag: orm.Mapped[str] = orm.mapped_column(sa.String)
    size: orm.Mapped[int] = orm.mapped_column(sa.Integer, index=True)
    meta: orm.Mapped[str] = orm.mapped_column(sqlite.JSON)
    tags: orm.Mapped[str] = orm.mapped_column(sqlite.JSON)
    update_time: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime)
    expire_time: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime, index=True)


class LoadedS3Dir(Base):
    __tablename__ = "loaded_s3_dir"

    uri: orm.Mapped[str] = orm.mapped_column(sa.String, primary_key=True)
    expire: orm.Mapped[int] = orm.mapped_column(sa.Integer)
    start_time: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime)
    end_time: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime)
    expire_time: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime)
    n_object: orm.Mapped[int] = orm.mapped_column(sa.Integer)

    def is_expired(self) -> bool:
        utc_now = datetime.utcnow()
        return utc_now >= self.expire_time


@dataclasses.dataclass
class S3Database:
    """
    The abstract S3 database for searching.

    :param engine: an sqlalchemy.engine.Engine object.
        See https://docs.sqlalchemy.org/en/latest/core/engines.html#sqlite.

    - read :meth:`S3Database.load_s3dir` to learn how load s3 information to the database.
    - read :meth:`S3Database.query` to learn how to search.
    """

    engine: sa.engine = dataclasses.field()

    def __post_init__(self):
        Base.metadata.create_all(self.engine)

    def clear(self):
        """
        Delete all cached data.
        """
        with orm.Session(self.engine) as ses:
            ses.execute(sa.delete(LoadedS3Dir))
            ses.execute(sa.delete(S3Object))
            ses.commit()

    def clear_s3dir(
        self,
        s3dir_uri: str,
    ):
        """
        Delete cached data of a specific S3 directory.
        """
        s3dir_md5 = get_md5(s3dir_uri)
        with orm.Session(self.engine) as ses:
            stmt = sa.delete(LoadedS3Dir).where(LoadedS3Dir.uri == s3dir_uri)
            ses.execute(stmt)
            stmt = sa.delete(S3Object).where(S3Object.s3dir_md5 == s3dir_md5)
            ses.execute(stmt)
            ses.commit()

    def load_s3dir(
        self,
        s3dir_uri: str,
        s3_client: "S3Client",
        ignore_expire: bool = False,
        ignore_metadata: bool = False,
        ignore_tags: bool = False,
        ignore_client_error: bool = False,
        expire: int = 900,
        limit: int = NOTHING,
    ) -> int:
        """
        Load s3 object from only one s3 directory. It will list all objects
        in s3dir_uri and store their information in the database.

        .. note::

            If you have a lot of s3 objects and you need to store their tags
            in the database, then it may take a long time.

        :param s3dir_uri: the uri of the s3 directory (or prefix).
        :param s3_client: the boto3.client("s3") object.
        :param ignore_expire: if True, we force reload the s3 directory even
            if it is not expired.
        :param ignore_metadata: if True, we don't load the metadata of the s3 object
            into the database.
        :param ignore_tags: if True, we don't load the tags of the s3 object
            into the database.
        :param ignore_client_error: if True, we skip the s3 object that failed
            to load the metadata or tags.
        :param expire: expire time in seconds.
        """
        s3dir = S3Path(s3dir_uri)
        s3dir_md5 = get_md5(s3dir_uri)

        with orm.Session(self.engine) as ses:
            stmt = sa.select(LoadedS3Dir).where(LoadedS3Dir.uri == s3dir.uri)
            cached_s3_dir: T.Optional[LoadedS3Dir] = ses.scalars(stmt).one_or_none()
            if cached_s3_dir is not None:
                # if expired, we need reload
                if cached_s3_dir.is_expired():
                    reload = True
                else:
                    # if not expired, and we ignore expire, we reload anyway
                    if ignore_expire:  # pragma: no cover
                        reload = True
                    # otherwise we don't reload
                    else:
                        reload = False

                if reload is False:
                    return 0

                stmt = sa.delete(LoadedS3Dir).where(LoadedS3Dir.uri == s3dir.uri)
                ses.execute(stmt)
                stmt = sa.delete(S3Object).where(S3Object.s3dir_md5 == s3dir_md5)
                ses.execute(stmt)

            s3obj_list = list()
            start_time = datetime.utcnow()
            expire_time = start_time + timedelta(seconds=expire)

            if (ignore_metadata is True) and (ignore_tags is True):  # pragma: no cover
                for ith, s3path in enumerate(
                    s3dir.iter_objects(bsm=s3_client, limit=limit), start=1
                ):
                    # print(f"loading {ith}: {s3path.uri}")
                    s3obj = S3Object(
                        uri=s3path.uri,
                        s3dir_md5=s3dir_md5,
                        bucket=s3path.bucket,
                        key=s3path.key,
                        dirpath=s3path.dirpath,
                        dirname=s3path.dirname,
                        basename=s3path.basename,
                        fname=s3path.fname,
                        ext=s3path.ext,
                        obj_update_at=s3path.last_modified_at,
                        etag=s3path.etag,
                        size=s3path.size,
                        meta={},
                        tags={},
                        update_time=start_time,
                        expire_time=expire_time,
                    )
                    s3obj_list.append(s3obj)
            else:
                for ith, s3path in enumerate(
                    s3dir.iter_objects(bsm=s3_client, limit=limit),
                    start=1,
                ):
                    # print(f"loading {ith} th: {s3path.uri}")
                    if ignore_metadata is False:
                        try:
                            s3path.head_object(s3_client)
                        except Exception as e:  # pragma: no cover
                            if ignore_client_error:
                                continue
                            else:
                                raise e
                        meta = s3path.metadata
                    else:
                        meta = {}
                    if ignore_tags is False:
                        try:
                            tags = s3path.get_tags(bsm=s3_client)[1]
                        except Exception as e:  # pragma: no cover
                            if ignore_client_error:
                                continue
                            else:
                                raise e
                    s3obj = S3Object(
                        uri=s3path.uri,
                        s3dir_md5=s3dir_md5,
                        bucket=s3path.bucket,
                        key=s3path.key,
                        dirpath=s3path.dirpath,
                        dirname=s3path.dirname,
                        basename=s3path.basename,
                        fname=s3path.fname,
                        ext=s3path.ext,
                        obj_update_at=s3path.last_modified_at,
                        etag=s3path.etag,
                        size=s3path.size,
                        meta=meta,
                        tags=tags,
                        update_time=start_time,
                        expire_time=expire_time,
                    )
                    s3obj_list.append(s3obj)

            end_time = datetime.utcnow()
            ses.add_all(s3obj_list)
            n_object = len(s3obj_list)

            cached_s3dir = LoadedS3Dir(
                uri=s3dir.uri,
                expire=expire,
                start_time=start_time,
                end_time=end_time,
                expire_time=expire_time,
                n_object=n_object,
            )
            ses.add(cached_s3dir)
            ses.commit()

        return n_object

    def load_many_s3dir(
        self,
        s3dir_uri_list: T.List[str],
        s3_client: T.Union["S3Client", T.List["S3Client"]],
        ignore_expire: bool = False,
        ignore_metadata: bool = False,
        ignore_tags: bool = False,
        ignore_client_error: bool = False,
        expire: int = 900,
        limit: int = NOTHING,
    ) -> int:
        """
        Load all s3 object from s3dir_uri_list.

        :param s3dir_uri_list: the list uri of the s3 directory (or prefix).
        :param s3_client: single or list of boto3.client("s3") object.
            If single, the s3dir_uri_list will use the same s3_client.
            If list, the list of s3dir_uri_list will be loaded with corresponding
            s3_client.
        :param ignore_expire: if True, we force reload the s3 directory even
            if it is not expired.
        :param ignore_metadata: if True, we don't load the metadata of the s3 object
            into the database.
        :param ignore_tags: if True, we don't load the tags of the s3 objects
            into the database.
        :param ignore_client_error: if True, we skip the s3 object that failed
            to load the metadata or tags.
        :param expire: expire time in seconds.
        """
        if isinstance(s3_client, list):
            if len(s3dir_uri_list) != len(s3_client):  # pragma: no cover
                raise ValueError("s3dir_uri_list and s3_client must have same length")
            else:
                pairs = zip(s3dir_uri_list, s3_client)
        else:
            pairs = ((s3dir, s3_client) for s3dir in s3dir_uri_list)

        n_object = 0
        for s3dir_uri, s3_client in pairs:
            n_object += self.load_s3dir(
                s3dir_uri=s3dir_uri,
                s3_client=s3_client,
                ignore_expire=ignore_expire,
                ignore_metadata=ignore_metadata,
                ignore_tags=ignore_tags,
                ignore_client_error=ignore_client_error,
                expire=expire,
                limit=limit,
            )

        return n_object

    def loaded_s3dir_list(
        self,
        return_entity: bool = False,
    ) -> T.List[T.Union[LoadedS3Dir, T.Dict[str, T.Any]]]:
        """
        Return list of all loaded s3dir.

        :param return_entity: if True, return :class:`S3Object`, otherwise, return dict
        """
        stmt = sa.select(LoadedS3Dir)
        if return_entity:
            with orm.Session(self.engine) as ses:
                return ses.scalars(stmt).all()
        else:
            with self.engine.connect() as conn:
                return list(conn.execute(stmt).mappings())

    def s3object_list(
        self,
        return_entity: bool = False,
    ) -> T.List[T.Union[S3Object, T.Dict[str, T.Any]]]:
        """
        Return list of all cached s3object.

        :param return_entity: if True, return :class:`S3Object`, otherwise, return dict
        """
        stmt = sa.select(S3Object)
        if return_entity:
            with orm.Session(self.engine) as ses:
                return ses.scalars(stmt).all()
        else:
            with self.engine.connect() as conn:
                return list(conn.execute(stmt).mappings())

    def query(
        self,
        stmt: sa.Select,
        return_entity: bool = False,
    ) -> T.Iterable[T.Union[LoadedS3Dir, T.Dict[str, T.Any]]]:
        """
        Run query statement, and yield results.

        :param return_entity: if True, return :class:`S3Object`, otherwise, return dict

        Example query statement::

            >>> import sqlalchemy as sa
            # select all
            >>> stmt = sa.select(S3Object)
            # filter by bucket
            >>> stmt = sa.select(S3Object).where(S3Object.bucket == "my-bucket")
            # filter by loaded s3 dir
            >>> stmt = sa.select(S3Object).where(S3Object.s3dir_md5 == get_md5("s3://my-bucket/"))
            # filter by multiple criterion
            >>> stmt = sa.select(S3Object).where(S3Object.ext == ".json", S3Object.size > 1000000)
            # filter by prefix
            >>> stmt = sa.select(S3Object).where(S3Object.key.startswith("folder"))
            # filter by expire time (not expired object only)
            >>> stmt = sa.select(S3Object).where(S3Object.expire_time <= datetime.utcnow()
            # filter by metadata
            >>> stmt = sa.select(S3Object).where(S3Object.meta["key"].as_string() == "value")
            # filter by tag
            >>> stmt = sa.select(S3Object).where(S3Object.tags["key"].as_string() == "value")
        """
        if return_entity:
            with orm.Session(self.engine) as ses:
                yield from ses.scalars(stmt)
        else:
            with self.engine.connect() as conn:
                yield from conn.execute(stmt).mappings()
