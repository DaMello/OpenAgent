class GitHubConnector:
    """GitHub connector scaffold.

    Planned capabilities: repository read/search, branches, commits, issues, and pull requests.
    Write actions should pass through the permission engine.
    """

    status = "not_configured"

    def connect(self) -> None:
        raise NotImplementedError("GitHub connector is planned for OpenAgent v0.2")
