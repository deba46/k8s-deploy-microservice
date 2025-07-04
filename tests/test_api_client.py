from unittest.mock import patch, Mock
import microservice_client 


@patch("microservice_client.requests.post")
def test_deploy_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.text = '{"message":"Pod deployment initiated"}'

    microservice_client.deploy()

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == f"{microservice_client .BASE_URL}/deploy"
    assert kwargs["json"] == {"namespace":  microservice_client.NAMESPACE, "image": microservice_client.IMAGE_NAME}
    assert kwargs["headers"] == {"Content-Type": "application/json"}


@patch("microservice_client.requests.get")
def test_check_status_running(mock_get):
    # Mock a successful pod status response showing "Running"
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"pod_status": "Running"}

    result = microservice_client.check_status(timeout_seconds=10, interval_seconds=1)
    assert result is True

@patch("microservice_client.requests.get")
def test_check_status_not_found_then_running(mock_get):
    response_404 = Mock()
    response_404.status_code = 404
    response_404.text = '{"detail": "Not Found"}'
    # 
    response_200 = Mock()
    response_200.status_code = 200
    response_200.text = '{"pod_status": "Running"}'
    response_200.json.return_value = {"pod_status": "Running"}

    mock_get.side_effect = [response_404, response_200]
    result = microservice_client.check_status(timeout_seconds=10, interval_seconds=1)
    assert result is True

@patch("microservice_client.requests.get")
def test_check_status_timeout(mock_get):
    mock_get.return_value.status_code = 404
    mock_get.return_value.text = '{"detail":"Not Found"}'

    result = microservice_client.check_status(timeout_seconds=3, interval_seconds=1)
    assert result is None  
