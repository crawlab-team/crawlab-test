from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class FileSyncRequest(_message.Message):
    __slots__ = ("spider_id", "path", "node_key")
    SPIDER_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    NODE_KEY_FIELD_NUMBER: _ClassVar[int]
    spider_id: str
    path: str
    node_key: str
    def __init__(self, spider_id: str | None = ..., path: str | None = ..., node_key: str | None = ...) -> None: ...

class FileInfo(_message.Message):
    __slots__ = ("name", "path", "full_path", "extension", "is_dir", "file_size", "mod_time", "mode", "hash")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    FULL_PATH_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    IS_DIR_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    MOD_TIME_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    name: str
    path: str
    full_path: str
    extension: str
    is_dir: bool
    file_size: int
    mod_time: int
    mode: int
    hash: str
    def __init__(
        self,
        name: str | None = ...,
        path: str | None = ...,
        full_path: str | None = ...,
        extension: str | None = ...,
        is_dir: bool = ...,
        file_size: int | None = ...,
        mod_time: int | None = ...,
        mode: int | None = ...,
        hash: str | None = ...,
    ) -> None: ...

class FileScanChunk(_message.Message):
    __slots__ = ("files", "is_complete", "error", "total_files")
    FILES_FIELD_NUMBER: _ClassVar[int]
    IS_COMPLETE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FILES_FIELD_NUMBER: _ClassVar[int]
    files: _containers.RepeatedCompositeFieldContainer[FileInfo]
    is_complete: bool
    error: str
    total_files: int
    def __init__(
        self,
        files: _Iterable[FileInfo | _Mapping] | None = ...,
        is_complete: bool = ...,
        error: str | None = ...,
        total_files: int | None = ...,
    ) -> None: ...

class FileDownloadRequest(_message.Message):
    __slots__ = ("spider_id", "path", "node_key")
    SPIDER_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    NODE_KEY_FIELD_NUMBER: _ClassVar[int]
    spider_id: str
    path: str
    node_key: str
    def __init__(self, spider_id: str | None = ..., path: str | None = ..., node_key: str | None = ...) -> None: ...

class FileDownloadChunk(_message.Message):
    __slots__ = ("data", "is_complete", "error", "total_bytes")
    DATA_FIELD_NUMBER: _ClassVar[int]
    IS_COMPLETE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BYTES_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    is_complete: bool
    error: str
    total_bytes: int
    def __init__(
        self,
        data: bytes | None = ...,
        is_complete: bool = ...,
        error: str | None = ...,
        total_bytes: int | None = ...,
    ) -> None: ...
