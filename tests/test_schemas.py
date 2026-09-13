from app.schemas import AgentResponse


def test_agent_response_success():
    response = AgentResponse(
        success=True,
        action="create_url",
        message="URL created successfully.",
        data={
            "short_code": "abc123",
        },
    )

    assert response.success is True
    assert response.action == "create_url"
    assert response.message == "URL created successfully."
    assert response.data["short_code"] == "abc123"


def test_agent_response_error():
    response = AgentResponse(
        success=False,
        message="Could not understand request.",
    )

    assert response.success is False
    assert response.action is None
    assert response.data is None
