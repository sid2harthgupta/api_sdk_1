# agent_eval_sdk.py
"""
AI Agent Evaluation Platform SDK

A Python SDK for evaluating AI agents against standardized test suites.

Installation:
    ```bash
    pip install agent-eval-sdk
    ```

Quick Start:
    ```python
    from agent_eval_sdk import EvalClient

    client = EvalClient(api_key="your_api_key")
    results = client.quick_evaluate("My Agent", "gpt-4")
    print(f"Score: {results.overall_score}")
    ```

Examples:
    Basic evaluation flow::

        >>> client = EvalClient(api_key="test_key")
        >>> agent = client.agents.create(name="Test Agent", model="gpt-4")
        >>> evaluation = client.evaluations.create(agent.id, "suite_001")
        >>> results = evaluation.wait_for_completion()
        >>> print(results.overall_score)
        0.875
"""

import time
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import requests
from enum import Enum

__version__ = "2.0.0"
__author__ = "Evaluation Platform Team"
__all__ = [
    "EvalClient",
    "Agent",
    "TestSuite",
    "Evaluation",
    "EvaluationResults",
    "EvalStatus",
    "EvalException"
]

# Configuration defaults
DEFAULT_BASE_URL = "http://localhost:5000/v1"
DEFAULT_TIMEOUT = 30
POLLING_INTERVAL = 2


class EvalException(Exception):
    """Base exception for all SDK errors.

    Attributes:
        message: Human-readable error message
        code: Error code for programmatic handling
        details: Additional error details
    """

    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class EvalStatus(Enum):
    """Evaluation status enumeration.

    Possible evaluation states:
        - PENDING: Evaluation queued but not started
        - RUNNING: Evaluation currently executing
        - COMPLETED: Evaluation finished successfully
        - FAILED: Evaluation encountered an error
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Agent:
    """Represents an AI agent in the evaluation platform.

    An Agent is the AI system being evaluated. Each agent has a unique
    identifier and metadata about its model and configuration.

    Attributes:
        id: Unique identifier for the agent
        name: Human-readable name for the agent
        model: Model identifier (e.g., "gpt-4", "claude-2")
        version: Version string for the agent
        description: Optional description of the agent
        metadata: Custom metadata dictionary
        created_at: ISO 8601 timestamp of creation
        organization: Organization that owns this agent

    Examples:
        Creating an agent::

            >>> agent = client.agents.create(
            ...     name="Production Agent",
            ...     model="gpt-4",
            ...     version="2.0.0",
            ...     metadata={"team": "ml-eng"}
            ... )
            >>> print(agent.id)
            'agent_abc123'
    """
    id: str
    name: str
    model: str
    version: str
    description: str
    metadata: Dict[str, Any]
    created_at: str
    organization: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create an Agent instance from a dictionary.

        Args:
            data: Dictionary containing agent data

        Returns:
            Agent instance

        Raises:
            KeyError: If required fields are missing
        """
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation.

        Returns:
            Dictionary containing all agent attributes
        """
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "version": self.version,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "organization": self.organization
        }


@dataclass
class TestSuite:
    """Represents a collection of evaluation tests.

    Test suites are curated collections of tasks designed to evaluate
    specific capabilities of AI agents.

    Attributes:
        id: Unique identifier for the test suite
        name: Human-readable name
        description: Description of what the suite tests
        test_count: Number of individual tests in the suite
        categories: List of capability categories tested
        created_at: ISO 8601 timestamp of creation

    Examples:
        Listing available test suites::

            >>> suites = client.test_suites.list()
            >>> for suite in suites:
            ...     print(f"{suite.name}: {suite.test_count} tests")
            Basic Reasoning: 25 tests
            Code Generation: 50 tests
    """
    id: str
    name: str
    description: str
    test_count: int
    categories: List[str]
    created_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestSuite':
        """Create a TestSuite instance from a dictionary.

        Args:
            data: Dictionary containing test suite data

        Returns:
            TestSuite instance
        """
        return cls(**data)


@dataclass
class EvaluationResults:
    """Results from a completed evaluation.

    Contains performance metrics and scores from an evaluation run.

    Attributes:
        overall_score: Aggregate score from 0.0 to 1.0
        passed_tests: Number of tests passed
        failed_tests: Number of tests failed
        categories: Score breakdown by category
        execution_time_seconds: Total execution time

    Examples:
        Analyzing results::

            >>> results = evaluation.wait_for_completion()
            >>> print(f"Score: {results.overall_score:.1%}")
            Score: 87.5%
            >>> print(f"Pass rate: {results.passed_tests}/{results.passed_tests + results.failed_tests}")
            Pass rate: 22/25
    """
    overall_score: float
    passed_tests: int
    failed_tests: int
    categories: Dict[str, float]
    execution_time_seconds: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvaluationResults':
        """Create an EvaluationResults instance from a dictionary."""
        return cls(**data)

    @property
    def pass_rate(self) -> float:
        """Calculate the pass rate as a percentage.

        Returns:
            Pass rate from 0.0 to 1.0
        """
        total = self.passed_tests + self.failed_tests
        return self.passed_tests / total if total > 0 else 0.0

    def get_grade(self) -> str:
        """Get a letter grade based on the overall score.

        Returns:
            Letter grade (A+, A, B, C, D, or F)

        Examples:
            >>> results.overall_score = 0.92
            >>> results.get_grade()
            'A+'
        """
        if self.overall_score >= 0.9:
            return "A+"
        elif self.overall_score >= 0.85:
            return "A"
        elif self.overall_score >= 0.8:
            return "B"
        elif self.overall_score >= 0.7:
            return "C"
        elif self.overall_score >= 0.6:
            return "D"
        else:
            return "F"


class Evaluation:
    """Represents an evaluation run.

    An Evaluation tracks the execution of a test suite against an agent.
    It provides methods to monitor progress and retrieve results.

    Attributes:
        id: Unique evaluation identifier
        agent_id: ID of the agent being evaluated
        test_suite_id: ID of the test suite being run
        status: Current evaluation status
        config: Configuration parameters for the evaluation
        created_at: ISO 8601 timestamp of creation
        organization: Organization that owns this evaluation
        results: Results object (None until evaluation completes)

    Examples:
        Running and monitoring an evaluation::

            >>> evaluation = client.evaluations.create(
            ...     agent_id="agent_123",
            ...     test_suite_id="suite_001"
            ... )
            >>> evaluation.refresh()
            >>> print(evaluation.status)
            'running'
            >>> results = evaluation.wait_for_completion(timeout=300)

    Note:
        Evaluations run asynchronously. Use :meth:`wait_for_completion` to block
        until results are available, or :meth:`refresh` to poll status.
    """

    def __init__(self, client: 'EvalClient', data: Dict[str, Any]):
        """Initialize an Evaluation instance.

        Args:
            client: Parent EvalClient instance
            data: Evaluation data from API
        """
        self.client = client
        self.id = data["id"]
        self.agent_id = data["agent_id"]
        self.test_suite_id = data["test_suite_id"]
        self.status = data["status"]
        self.config = data.get("config", {})
        self.created_at = data["created_at"]
        self.organization = data["organization"]
        self.results: Optional[EvaluationResults] = None
        self._raw_data = data

    def refresh(self) -> 'Evaluation':
        """Refresh evaluation status from the API.

        Updates the local evaluation object with the latest status
        and results from the server.

        Returns:
            Self for method chaining

        Raises:
            EvalException: If the API request fails

        Examples:
            >>> evaluation.refresh()
            >>> if evaluation.status == "completed":
            ...     print(evaluation.results.overall_score)
        """
        data = self.client._get(f"/evaluations/{self.id}")
        self.status = data["status"]
        self._raw_data = data
        if "results" in data:
            self.results = EvaluationResults.from_dict(data["results"])
        return self

    def wait_for_completion(self, timeout: int = 300) -> EvaluationResults:
        """Wait for the evaluation to complete.

        Blocks until the evaluation finishes or the timeout is reached.
        Polls the API every 2 seconds for status updates.

        Args:
            timeout: Maximum seconds to wait (default: 300)

        Returns:
            EvaluationResults object containing scores and metrics

        Raises:
            TimeoutError: If evaluation doesn't complete within timeout
            EvalException: If evaluation fails

        Examples:
            >>> try:
            ...     results = evaluation.wait_for_completion(timeout=60)
            ...     print(f"Score: {results.overall_score}")
            ... except TimeoutError:
            ...     print("Evaluation took too long")
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            self.refresh()

            if self.status == EvalStatus.COMPLETED.value:
                if self.results is None:
                    raise EvalException("Evaluation completed but no results available")
                return self.results
            elif self.status == EvalStatus.FAILED.value:
                raise EvalException(f"Evaluation {self.id} failed")

            time.sleep(POLLING_INTERVAL)

        raise TimeoutError(f"Evaluation {self.id} timed out after {timeout} seconds")

    def cancel(self) -> bool:
        """Cancel a running evaluation.

        Returns:
            True if cancellation was successful

        Raises:
            EvalException: If cancellation fails

        Note:
            Not implemented in mock API
        """
        raise NotImplementedError("Cancellation not yet implemented")

    def to_dict(self) -> Dict[str, Any]:
        """Get the raw dictionary representation.

        Returns:
            Complete evaluation data as returned by the API
        """
        return self._raw_data


class AgentsAPI:
    """API client for agent management.

    Provides methods to create, retrieve, and manage agents.
    Access via `client.agents`.

    Examples:
        >>> client = EvalClient(api_key="key")
        >>> agent = client.agents.create(name="My Agent", model="gpt-4")
        >>> retrieved = client.agents.get(agent.id)
    """

    def __init__(self, client: 'EvalClient'):
        """Initialize the Agents API.

        Args:
            client: Parent EvalClient instance
        """
        self.client = client

    def create(self,
               name: str,
               model: str = "unknown",
               version: str = "1.0.0",
               description: str = "",
               metadata: Optional[Dict[str, Any]] = None) -> Agent:
        """Create a new agent.

        Args:
            name: Human-readable name for the agent
            model: Model identifier (e.g., "gpt-4", "claude-2")
            version: Version string for tracking iterations
            description: Optional description of the agent's purpose
            metadata: Custom key-value pairs for additional data

        Returns:
            Created Agent object with assigned ID

        Raises:
            EvalException: If creation fails

        Examples:
            >>> agent = client.agents.create(
            ...     name="Production Agent v2",
            ...     model="gpt-4",
            ...     version="2.1.0",
            ...     description="Improved reasoning capabilities",
            ...     metadata={"team": "ml-eng", "experiment": "reasoning-v2"}
            ... )
        """
        data = self.client._post("/agents", {
            "name": name,
            "model": model,
            "version": version,
            "description": description,
            "metadata": metadata or {}
        })
        return Agent.from_dict(data)

    def get(self, agent_id: str) -> Agent:
        """Retrieve an agent by ID.

        Args:
            agent_id: Unique identifier of the agent

        Returns:
            Agent object

        Raises:
            EvalException: If agent not found or request fails

        Examples:
            >>> agent = client.agents.get("agent_abc123")
            >>> print(agent.name)
        """
        data = self.client._get(f"/agents/{agent_id}")
        return Agent.from_dict(data)

    def list(self, limit: int = 100) -> List[Agent]:
        """List agents in your organization.

        Args:
            limit: Maximum number of agents to return

        Returns:
            List of Agent objects

        Note:
            Not implemented in mock API
        """
        raise NotImplementedError("Agent listing not yet implemented")


class TestSuitesAPI:
    """API client for test suite management.

    Provides methods to list and retrieve available test suites.
    Access via `client.test_suites`.

    Examples:
        >>> suites = client.test_suites.list()
        >>> suite = client.test_suites.get("suite_001")
    """

    def __init__(self, client: 'EvalClient'):
        """Initialize the Test Suites API.

        Args:
            client: Parent EvalClient instance
        """
        self.client = client

    def list(self) -> List[TestSuite]:
        """List all available test suites.

        Returns:
            List of TestSuite objects

        Raises:
            EvalException: If request fails

        Examples:
            >>> suites = client.test_suites.list()
            >>> for suite in suites:
            ...     print(f"{suite.id}: {suite.name} ({suite.test_count} tests)")
        """
        data = self.client._get("/test-suites")
        return [TestSuite.from_dict(suite) for suite in data["test_suites"]]

    def get(self, suite_id: str) -> Optional[TestSuite]:
        """Get a specific test suite by ID.

        Args:
            suite_id: Unique identifier of the test suite

        Returns:
            TestSuite object if found, None otherwise

        Examples:
            >>> suite = client.test_suites.get("suite_001")
            >>> if suite:
            ...     print(suite.description)
        """
        suites = self.list()
        for suite in suites:
            if suite.id == suite_id:
                return suite
        return None


class EvaluationsAPI:
    """API client for evaluation management.

    Provides methods to create, retrieve, and list evaluations.
    Access via `client.evaluations`.

    Examples:
        >>> evaluation = client.evaluations.create("agent_123", "suite_001")
        >>> results = evaluation.wait_for_completion()
    """

    def __init__(self, client: 'EvalClient'):
        """Initialize the Evaluations API.

        Args:
            client: Parent EvalClient instance
        """
        self.client = client

    def create(self,
               agent_id: str,
               test_suite_id: str,
               config: Optional[Dict[str, Any]] = None) -> Evaluation:
        """Create a new evaluation run.

        Starts an asynchronous evaluation of an agent against a test suite.

        Args:
            agent_id: ID of the agent to evaluate
            test_suite_id: ID of the test suite to run
            config: Optional configuration parameters

        Returns:
            Evaluation object for monitoring progress

        Raises:
            EvalException: If creation fails

        Examples:
            Basic evaluation::

                >>> evaluation = client.evaluations.create(
                ...     agent_id="agent_123",
                ...     test_suite_id="suite_001"
                ... )

            With configuration::

                >>> evaluation = client.evaluations.create(
                ...     agent_id="agent_123",
                ...     test_suite_id="suite_001",
                ...     config={
                ...         "timeout": 60,
                ...         "parallel": True,
                ...         "temperature": 0.7
                ...     }
                ... )
        """
        data = self.client._post("/evaluations", {
            "agent_id": agent_id,
            "test_suite_id": test_suite_id,
            "config": config or {}
        })
        return Evaluation(self.client, data)

    def get(self, eval_id: str) -> Evaluation:
        """Retrieve an evaluation by ID.

        Args:
            eval_id: Unique identifier of the evaluation

        Returns:
            Evaluation object

        Raises:
            EvalException: If evaluation not found

        Examples:
            >>> evaluation = client.evaluations.get("eval_abc123")
            >>> print(evaluation.status)
        """
        data = self.client._get(f"/evaluations/{eval_id}")
        return Evaluation(self.client, data)

    def list(self,
             page: int = 1,
             limit: int = 10,
             status: Optional[str] = None) -> Dict[str, Any]:
        """List evaluations with pagination.

        Args:
            page: Page number (1-indexed)
            limit: Results per page (max 100)
            status: Filter by status (optional)

        Returns:
            Dictionary containing evaluations and pagination info

        Examples:
            >>> response = client.evaluations.list(page=1, limit=20)
            >>> for eval in response["evaluations"]:
            ...     print(f"{eval['id']}: {eval['status']}")
        """
        params = f"page={page}&limit={min(limit, 100)}"
        if status:
            params += f"&status={status}"
        return self.client._get(f"/evaluations?{params}")


class WebhooksAPI:
    """API client for webhook management.

    Provides methods to register webhooks for evaluation events.
    Access via `client.webhooks`.

    Examples:
        >>> webhook = client.webhooks.create(
        ...     url="https://myapp.com/webhook",
        ...     events=["evaluation.completed"]
        ... )
    """

    def __init__(self, client: 'EvalClient'):
        """Initialize the Webhooks API.

        Args:
            client: Parent EvalClient instance
        """
        self.client = client

    def create(self,
               url: str,
               events: Optional[List[str]] = None) -> Dict[str, Any]:
        """Register a webhook endpoint.

        Args:
            url: HTTPS URL to receive webhook events
            events: List of event types to subscribe to

        Returns:
            Dictionary containing webhook ID and configuration

        Raises:
            EvalException: If registration fails

        Examples:
            >>> webhook = client.webhooks.create(
            ...     url="https://myapp.com/webhooks/evaluations",
            ...     events=["evaluation.completed", "evaluation.failed"]
            ... )

        Available Events:
            - evaluation.started: Evaluation begins processing
            - evaluation.completed: Evaluation finishes successfully
            - evaluation.failed: Evaluation encounters an error
        """
        return self.client._post("/webhooks", {
            "url": url,
            "events": events or ["evaluation.completed"]
        })


class EvalClient:
    """Main client for interacting with the AI Agent Evaluation Platform.

    This is the primary entry point for the SDK. Initialize with your API key
    to access all platform functionality.

    Attributes:
        agents: Agent management API
        test_suites: Test suite discovery API
        evaluations: Evaluation management API
        webhooks: Webhook management API

    Args:
        api_key: Your API authentication key
        base_url: API endpoint URL (default: http://localhost:5000/v1)
        timeout: Request timeout in seconds (default: 30)

    Examples:
        Basic initialization::

            >>> from agent_eval_sdk import EvalClient
            >>> client = EvalClient(api_key="your_api_key")

        With custom configuration::

            >>> client = EvalClient(
            ...     api_key="your_api_key",
            ...     base_url="https://api.eval.ai/v1",
            ...     timeout=60
            ... )

        Quick evaluation::

            >>> results = client.quick_evaluate(
            ...     agent_name="My Agent",
            ...     agent_model="gpt-4"
            ... )
            >>> print(f"Score: {results.overall_score:.1%}")

    Raises:
        EvalException: If initialization fails
    """

    def __init__(self,
                 api_key: str,
                 base_url: str = DEFAULT_BASE_URL,
                 timeout: int = DEFAULT_TIMEOUT):
        """Initialize the evaluation client.

        Args:
            api_key: Your API authentication key
            base_url: API endpoint URL
            timeout: Request timeout in seconds

        Raises:
            ValueError: If api_key is empty
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json',
            'User-Agent': f'agent-eval-sdk/{__version__}'
        })

        # Initialize API modules
        self.agents = AgentsAPI(self)
        self.test_suites = TestSuitesAPI(self)
        self.evaluations = EvaluationsAPI(self)
        self.webhooks = WebhooksAPI(self)

    def _request(self,
                 method: str,
                 endpoint: str,
                 data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to API.

        Internal method for API communication.

        Args:
            method: HTTP method (GET or POST)
            endpoint: API endpoint path
            data: Request body for POST requests

        Returns:
            JSON response as dictionary

        Raises:
            EvalException: If request fails
        """
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = self.session.get(url, timeout=self.timeout)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")

            if response.status_code == 401:
                raise EvalException("Invalid API key", code="AUTH_ERROR")
            elif response.status_code == 404:
                raise EvalException(f"Resource not found: {endpoint}", code="NOT_FOUND")
            elif response.status_code >= 500:
                raise EvalException("Server error", code="SERVER_ERROR")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise EvalException(f"Request timed out after {self.timeout}s", code="TIMEOUT")
        except requests.exceptions.ConnectionError:
            raise EvalException("Connection failed", code="CONNECTION_ERROR")
        except requests.exceptions.RequestException as e:
            raise EvalException(f"API request failed: {str(e)}", code="REQUEST_ERROR")

    def _get(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request.

        Args:
            endpoint: API endpoint path

        Returns:
            JSON response
        """
        return self._request("GET", endpoint)

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request.

        Args:
            endpoint: API endpoint path
            data: Request body

        Returns:
            JSON response
        """
        return self._request("POST", endpoint, data)

    def health_check(self) -> Dict[str, Any]:
        """Check API health status.

        Verifies connectivity and gets API version information.

        Returns:
            Dictionary with status, version, and timestamp

        Examples:
            >>> health = client.health_check()
            >>> print(f"API Status: {health['status']}")
            >>> print(f"Version: {health['version']}")
        """
        return self._get("/health")

    def quick_evaluate(self,
                       agent_name: str,
                       agent_model: str,
                       test_suite_id: str = "suite_001",
                       wait: bool = True) -> Union[EvaluationResults, Evaluation]:
        """Convenience method for quick evaluation.

        Creates an agent and immediately runs an evaluation. Useful for
        one-off tests or getting started quickly.

        Args:
            agent_name: Name for the agent
            agent_model: Model identifier (e.g., "gpt-4")
            test_suite_id: Test suite to run (default: "suite_001")
            wait: If True, wait for completion; if False, return Evaluation object

        Returns:
            EvaluationResults if wait=True, Evaluation object if wait=False

        Raises:
            EvalException: If any step fails
            TimeoutError: If evaluation times out (when wait=True)

        Examples:
            Synchronous (blocking)::

                >>> results = client.quick_evaluate(
                ...     agent_name="Test Agent",
                ...     agent_model="gpt-4"
                ... )
                >>> print(f"Score: {results.overall_score:.1%}")

            Asynchronous (non-blocking)::

                >>> evaluation = client.quick_evaluate(
                ...     agent_name="Test Agent",
                ...     agent_model="gpt-4",
                ...     wait=False
                ... )
                >>> # Do other work...
                >>> results = evaluation.wait_for_completion()
        """
        # Create agent
        agent = self.agents.create(name=agent_name, model=agent_model)

        # Start evaluation
        evaluation = self.evaluations.create(agent.id, test_suite_id)

        if wait:
            # Wait for results
            return evaluation.wait_for_completion()
        else:
            # Return evaluation object for async handling
            return evaluation

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"EvalClient(base_url='{self.base_url}')"


# Utility functions
def get_client_from_env() -> EvalClient:
    """Create a client using environment variables.

    Reads configuration from:
        - EVAL_API_KEY: API authentication key (required)
        - EVAL_API_URL: API base URL (optional)
        - EVAL_TIMEOUT: Request timeout in seconds (optional)

    Returns:
        Configured EvalClient instance

    Raises:
        ValueError: If EVAL_API_KEY is not set

    Examples:
        >>> import os
        >>> os.environ['EVAL_API_KEY'] = 'your_key'
        >>> client = get_client_from_env()
    """
    import os

    api_key = os.environ.get("EVAL_API_KEY")
    if not api_key:
        raise ValueError("EVAL_API_KEY environment variable not set")

    base_url = os.environ.get("EVAL_API_URL", DEFAULT_BASE_URL)
    timeout = int(os.environ.get("EVAL_TIMEOUT", DEFAULT_TIMEOUT))

    return EvalClient(api_key=api_key, base_url=base_url, timeout=timeout)


if __name__ == "__main__":
    # Example usage when running directly
    print(f"Agent Evaluation SDK v{__version__}")
    print("Run 'python -m pydoc agent_eval_sdk' to view documentation")
