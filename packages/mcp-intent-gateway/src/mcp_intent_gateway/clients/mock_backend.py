"""Mock backend client for calling the backend API."""

import logging
import os
from typing import Any

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

DEFAULT_BACKEND_URL = "http://localhost:3001"


class Child(BaseModel):
    """Child entity from the backend."""

    id: int = Field(..., description="Unique child identifier")
    firstname: str = Field(..., description="Child's first name")


class EventResponse(BaseModel):
    """Response from creating an event."""

    success: bool = Field(..., description="Whether the event was created")
    message: str = Field(..., description="Response message")
    mock_id: str | None = Field(default=None, description="Mock event ID")
    timestamp: str | None = Field(default=None, description="Event timestamp")


class MockBackendClient:
    """
    Client for communicating with the mock backend API.

    This client provides methods to:
    - Get child by firstname (mocked - returns deterministic ID)
    - Add events for a child
    """

    def __init__(self, base_url: str | None = None) -> None:
        """
        Initialize the mock backend client.

        Args:
            base_url: Base URL for the backend API. Defaults to BACKEND_URL env var
                      or http://localhost:3001
        """
        self.base_url = base_url or os.getenv("BACKEND_URL", DEFAULT_BACKEND_URL)

    async def get_child_by_firstname(self, firstname: str) -> Child | None:
        """
        Get a child by their first name.

        This is a MOCK implementation that returns a deterministic child ID
        based on the firstname hash. In a real implementation, this would
        call the actual backend API.

        Args:
            firstname: The child's first name

        Returns:
            Child object with id and firstname, or None if not found
        """
        # Mock implementation - generate deterministic ID from firstname
        # This ensures same name always returns same ID (deterministic)
        fake_id = abs(hash(firstname)) % 1000
        logger.debug(f"Mock: Resolved child '{firstname}' to ID {fake_id}")
        return Child(id=fake_id, firstname=firstname)

    async def add_event(
        self,
        child_id: int,
        action: str,
        properties: dict[str, Any],
    ) -> EventResponse:
        """
        Add an event for a child.

        Calls POST /child/{childId}/add_event on the backend.

        Args:
            child_id: The child's ID
            action: The action type (e.g., 'record_meal')
            properties: Event properties

        Returns:
            EventResponse with success status and details
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/child/{child_id}/add_event",
                    json={"action": action, "properties": properties},
                )

                if response.status_code == 200:
                    data = response.json()
                    return EventResponse(
                        success=True,
                        message=data.get("message", "Event created"),
                        mock_id=data.get("mockId"),
                        timestamp=data.get("timestamp"),
                    )
                else:
                    # Handle error response
                    return EventResponse(
                        success=False,
                        message=f"Backend error: {response.status_code}",
                    )

        except httpx.ConnectError as e:
            logger.warning(f"Cannot connect to backend at {self.base_url}: {e}")
            # Return mock success for development when backend is not running
            return EventResponse(
                success=True,
                message=f"Mock event created (backend unavailable) for child {child_id}",
                mock_id=f"mock-{child_id}-{hash(action) % 10000}",
            )
        except httpx.TimeoutException:
            return EventResponse(
                success=False,
                message="Backend request timed out",
            )
        except Exception as e:
            logger.error(f"Unexpected error calling backend: {e}")
            return EventResponse(
                success=False,
                message=f"Unexpected error: {str(e)}",
            )

    async def health_check(self) -> bool:
        """
        Check if the backend is healthy.

        Returns:
            True if backend is reachable and healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False
