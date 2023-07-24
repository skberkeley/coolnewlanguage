from unittest.mock import Mock, NonCallableMock

import pytest

from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.stage import process


class TestLambdaProcessor:
    def test_lambda_processor_handling_post_happy_path(self):
        # Setup
        # Mock a stage func
        mock_result = Mock()
        mock_func = Mock(return_value=mock_result)
        # Set handling_post to True
        process.handling_post = True

        # Do
        lambda_processor = LambdaProcessor(mock_func)

        # Verify
        # Check that mock_func was called
        mock_func.assert_called()
        # Check that the result was set
        assert lambda_processor.result == mock_result

        # Cleanup
        # Reset handling_post
        process.handling_post = False

    def test_lambda_processor_not_handling_post_happy_path(self):
        # Setup
        # Mock a stage func
        mock_func = Mock()

        # Do
        lambda_processor = LambdaProcessor(mock_func)

        # Verify
        # Check that mock_func was not called
        mock_func.assert_not_called()
        # Check that result is None
        assert lambda_processor.result is None

    def test_lambda_processor_not_callable_func(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected func to be callable"):
            LambdaProcessor(NonCallableMock())