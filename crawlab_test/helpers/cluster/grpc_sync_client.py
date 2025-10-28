#!/usr/bin/env python3
"""
gRPC Sync Client - Makes actual gRPC calls to test file sync service
"""

import socket
import time
from typing import Dict

import grpc

# Add paths for imports
from services import sync_service_pb2, sync_service_pb2_grpc


def verify_grpc_server_accessible(
    host: str = "localhost", port: int = 9666, max_retries: int = 10, logger=None
) -> Dict[str, any]:
    """
    Verify gRPC server is accessible before running tests.

    Args:
        host: Server hostname
        port: Server port
        max_retries: Maximum connection attempts
        logger: Optional logger for output

    Returns:
        dict: {
            'accessible': bool,
            'attempts': int,
            'error': Optional[str],
            'latency_ms': Optional[float]
        }
    """
    result = {"accessible": False, "attempts": 0, "error": None, "latency_ms": None}

    for attempt in range(1, max_retries + 1):
        result["attempts"] = attempt
        try:
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            connect_result = sock.connect_ex((host, port))
            sock.close()
            latency = (time.time() - start) * 1000

            if connect_result == 0:
                result["accessible"] = True
                result["latency_ms"] = round(latency, 2)
                if logger:
                    logger.info(f"✓ gRPC server accessible on {host}:{port} (latency: {result['latency_ms']}ms)")
                return result
            else:
                if logger:
                    logger.debug(f"Attempt {attempt}/{max_retries}: Connection refused (code {connect_result})")
        except socket.timeout:
            if logger:
                logger.debug(f"Attempt {attempt}/{max_retries}: Connection timeout")
            result["error"] = "Connection timeout"
        except Exception as e:
            if logger:
                logger.debug(f"Attempt {attempt}/{max_retries}: {type(e).__name__}: {e}")
            result["error"] = str(e)

        if attempt < max_retries:
            time.sleep(2)

    result["error"] = result.get("error") or f"Connection refused after {max_retries} attempts"
    if logger:
        logger.error(f"❌ gRPC server NOT accessible on {host}:{port} after {max_retries} attempts")
    return result


def test_grpc_connection(
    host: str = "localhost", port: int = 9666, spider_id: str = "test", logger=None
) -> Dict[str, any]:
    """
    Test actual gRPC connection and basic RPC call.

    Returns:
        dict: {
            'success': bool,
            'error': Optional[str],
            'error_code': Optional[str],
            'error_details': Optional[str]
        }
    """
    result = {"success": False, "error": None, "error_code": None, "error_details": None}

    client = None
    try:
        client = GrpcSyncClient(host=host, port=port)
        client.connect()

        # Try a simple scan with minimal timeout
        request = sync_service_pb2.FileSyncRequest(spider_id=spider_id, path="", node_key="connectivity-test")
        metadata = [("authorization", client.auth_key)]

        # Just check if we can establish connection and get first response
        response_stream = client.stub.StreamFileScan(request, metadata=metadata, timeout=5)
        next(response_stream)  # Get first chunk

        result["success"] = True
        if logger:
            logger.info("✓ gRPC connection test successful")

    except grpc.RpcError as e:
        result["error_code"] = e.code().name
        result["error_details"] = e.details()
        result["error"] = f"gRPC error: {e.code().name}: {e.details()}"
        if logger:
            logger.error(f"❌ gRPC RPC failed: {e.code().name}")
            logger.error(f"   Details: {e.details()}")
    except StopIteration:
        # Got first response but stream ended - still counts as success
        result["success"] = True
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e!s}"
        if logger:
            logger.error(f"❌ Connection test failed: {result['error']}")
    finally:
        if client:
            client.close()

    return result


class GrpcSyncClient:
    """Client to call Crawlab's gRPC SyncService"""

    def __init__(self, host="localhost", port=9666, auth_key="Crawlab2024!"):
        self.address = f"{host}:{port}"
        self.auth_key = auth_key
        self.channel = None
        self.stub = None

    def connect(self):
        """Establish gRPC connection"""
        self.channel = grpc.insecure_channel(self.address)
        self.stub = sync_service_pb2_grpc.SyncServiceStub(self.channel)

    def close(self):
        """Close gRPC connection"""
        if self.channel:
            self.channel.close()

    def stream_file_scan(self, spider_id, path="", node_key="test-worker"):
        """
        Call StreamFileScan RPC - returns streaming response

        Args:
            spider_id: Spider/workspace ID
            path: Subdirectory path (empty for root)
            node_key: Worker node identifier

        Returns:
            Iterator of FileScanChunk messages
        """
        request = sync_service_pb2.FileSyncRequest(spider_id=spider_id, path=path, node_key=node_key)

        # Add authorization metadata
        metadata = [("authorization", self.auth_key)]

        try:
            response_stream = self.stub.StreamFileScan(request, metadata=metadata, timeout=30)
            return response_stream
        except grpc.RpcError as e:
            error_msg = f"RPC failed: {e.code().name}: {e.details()}"
            print(error_msg)
            # Re-raise with more context
            raise RuntimeError(error_msg) from e

    def scan_files_full(self, spider_id, path="", node_key="test-worker"):
        """
        Complete file scan - consumes entire stream and returns all files

        Returns:
            dict with 'files', 'total', 'error', 'error_code', 'success'
        """
        all_files = []
        total_files = 0
        error = None
        error_code = None

        try:
            for chunk in self.stream_file_scan(spider_id, path, node_key):
                if chunk.error:
                    error = chunk.error
                    break

                all_files.extend(chunk.files)

                if chunk.is_complete:
                    total_files = chunk.total_files
                    break

            return {
                "files": all_files,
                "total": total_files,
                "error": error,
                "error_code": error_code,
                "success": error is None,
            }
        except grpc.RpcError as e:
            error_code = e.code().name
            error = f"{e.code().name}: {e.details()}"
            return {"files": [], "total": 0, "error": error, "error_code": error_code, "success": False}
        except Exception as e:
            return {"files": [], "total": 0, "error": str(e), "error_code": type(e).__name__, "success": False}


if __name__ == "__main__":
    # Quick test
    client = GrpcSyncClient()
    try:
        client.connect()
        print(f"✓ Connected to gRPC server at {client.address}")

        # Test with a simple spider ID
        result = client.scan_files_full("cls003-test", "")
        print(f"✓ Scan result: {result['total']} files, success={result['success']}")
        if result["error"]:
            print(f"  Error: {result['error']}")
        else:
            print(f"  First few files: {[f.name for f in result['files'][:3]]}")
    finally:
        client.close()
