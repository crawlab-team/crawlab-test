from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileSyncRequest(_message.Message):
    __slots__ = ("spider_id", "path", "node_key")
    SPIDER_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    NODE_KEY_FIELD_NUMBER: _ClassVar[int]
    spider_id: str
    path: str
    node_key: str
    def __init__(self, spider_id: _Optional[str] = ..., path: _Optional[str] = ..., node_key: _Optional[str] = ...) -> None: ...

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
    def __init__(self, name: _Optional[str] = ..., path: _Optional[str] = ..., full_path: _Optional[str] = ..., extension: _Optional[str] = ..., is_dir: bool = ..., file_size: _Optional[int] = ..., mod_time: _Optional[int] = ..., mode: _Optional[int] = ..., hash: _Optional[str] = ...) -> None: ...

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
    def __init__(self, files: _Optional[_Iterable[_Union[FileInfo, _Mapping]]] = ..., is_complete: bool = ..., error: _Optional[str] = ..., total_files: _Optional[int] = ...) -> None: ...

class FileDownloadRequest(_message.Message):
    __slots__ = ("spider_id", "path", "node_key")
    SPIDER_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    NODE_KEY_FIELD_NUMBER: _ClassVar[int]
    spider_id: str
    path: str
    node_key: str
    def __init__(self, spider_id: _Optional[str] = ..., path: _Optional[str] = ..., node_key: _Optional[str] = ...) -> None: ...

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
    def __init__(self, data: _Optional[bytes] = ..., is_complete: bool = ..., error: _Optional[str] = ..., total_bytes: _Optional[int] = ...) -> None: ...
