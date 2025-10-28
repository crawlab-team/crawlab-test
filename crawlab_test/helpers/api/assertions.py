"""
API Assertions Module

Provides common assertion utilities for API testing.
"""

from typing import Dict, Any, Optional, List


class APIAssertions:
    """Helper class for API response assertions."""
    
    @staticmethod
    def assert_success(response_data: Dict, message: str = "API call failed") -> bool:
        """
        Assert API response is successful.
        
        Args:
            response_data: Response data dictionary
            message: Error message if assertion fails
            
        Returns:
            True if successful
            
        Raises:
            AssertionError: If response indicates failure
        """
        if 'error' in response_data:
            raise AssertionError(f"{message}: {response_data['error']}")
        return True
    
    @staticmethod
    def assert_status_code(actual: int, expected: int, message: str = "Status code mismatch"):
        """Assert HTTP status code matches expected."""
        assert actual == expected, f"{message}: expected {expected}, got {actual}"
    
    @staticmethod
    def assert_has_field(data: Dict, field: str, message: Optional[str] = None):
        """Assert data contains a specific field."""
        msg = message or f"Expected field '{field}' not found in response"
        assert field in data, msg
    
    @staticmethod
    def assert_field_equals(data: Dict, field: str, expected: Any, message: Optional[str] = None):
        """Assert field value equals expected value."""
        APIAssertions.assert_has_field(data, field)
        actual = data[field]
        msg = message or f"Field '{field}' mismatch: expected {expected}, got {actual}"
        assert actual == expected, msg
    
    @staticmethod
    def assert_field_not_empty(data: Dict, field: str, message: Optional[str] = None):
        """Assert field exists and is not empty."""
        APIAssertions.assert_has_field(data, field)
        value = data[field]
        msg = message or f"Field '{field}' is empty"
        assert value, msg
    
    @staticmethod
    def assert_is_list(data: Any, message: str = "Expected list") -> bool:
        """Assert data is a list."""
        assert isinstance(data, list), f"{message}, got {type(data).__name__}"
        return True
    
    @staticmethod
    def assert_is_dict(data: Any, message: str = "Expected dictionary") -> bool:
        """Assert data is a dictionary."""
        assert isinstance(data, dict), f"{message}, got {type(data).__name__}"
        return True
    
    @staticmethod
    def assert_list_not_empty(data: List, message: str = "List is empty"):
        """Assert list is not empty."""
        APIAssertions.assert_is_list(data)
        assert len(data) > 0, message
    
    @staticmethod
    def assert_list_length(data: List, expected: int, message: Optional[str] = None):
        """Assert list has expected length."""
        APIAssertions.assert_is_list(data)
        actual = len(data)
        msg = message or f"List length mismatch: expected {expected}, got {actual}"
        assert actual == expected, msg
    
    @staticmethod
    def assert_contains(haystack: str, needle: str, message: Optional[str] = None):
        """Assert string contains substring."""
        msg = message or f"'{needle}' not found in string"
        assert needle in haystack, msg
    
    @staticmethod
    def assert_not_contains(haystack: str, needle: str, message: Optional[str] = None):
        """Assert string does not contain substring."""
        msg = message or f"'{needle}' found in string (should not be present)"
        assert needle not in haystack, msg
    
    @staticmethod
    def assert_task_status(status: str, expected: str, message: Optional[str] = None):
        """Assert task status matches expected."""
        msg = message or f"Task status mismatch: expected {expected}, got {status}"
        assert status == expected, msg
    
    @staticmethod
    def assert_task_success(status: str, message: str = "Task did not complete successfully"):
        """Assert task completed successfully."""
        assert status == "finished", f"{message}: status={status}"
    
    @staticmethod
    def assert_no_error(status: str, message: str = "Task failed with error"):
        """Assert task did not error."""
        assert status != "error", f"{message}: status={status}"
    
    @staticmethod
    def assert_id_format(id_value: str, message: str = "Invalid ID format"):
        """Assert ID is non-empty string."""
        assert isinstance(id_value, str), f"{message}: not a string"
        assert len(id_value) > 0, f"{message}: empty string"
    
    @staticmethod
    def assert_response_data(response_data: Dict, expected_type: type = dict, 
                           message: Optional[str] = None) -> Any:
        """
        Assert response has data field and return it.
        
        Args:
            response_data: Response data dictionary
            expected_type: Expected type of data field (dict, list, str, etc.)
            message: Optional error message
            
        Returns:
            The data field value
            
        Raises:
            AssertionError: If data field missing or wrong type
        """
        APIAssertions.assert_has_field(response_data, 'data', message)
        data = response_data['data']
        
        msg = message or f"Data field type mismatch: expected {expected_type.__name__}, got {type(data).__name__}"
        assert isinstance(data, expected_type), msg
        
        return data
    
    @staticmethod
    def assert_spider_exists(spider_data: Dict):
        """Assert spider data has required fields."""
        required_fields = ['_id', 'name', 'cmd']
        for field in required_fields:
            APIAssertions.assert_has_field(spider_data, field, 
                                          f"Spider missing required field: {field}")
    
    @staticmethod
    def assert_task_exists(task_data: Dict):
        """Assert task data has required fields."""
        required_fields = ['_id', 'spider_id', 'status']
        for field in required_fields:
            APIAssertions.assert_has_field(task_data, field, 
                                          f"Task missing required field: {field}")
    
    @staticmethod
    def assert_user_exists(user_data: Dict):
        """Assert user data has required fields."""
        required_fields = ['_id', 'username']
        for field in required_fields:
            APIAssertions.assert_has_field(user_data, field, 
                                          f"User missing required field: {field}")
