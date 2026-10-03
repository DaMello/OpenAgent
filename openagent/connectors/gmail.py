class GmailConnector:
    """OAuth-based Gmail connector scaffold.

    Planned capabilities: search, read, draft, reply, archive, and send.
    Sending should require explicit permission by default.
    """

    status = "not_configured"

    def connect(self) -> None:
        raise NotImplementedError("Gmail OAuth connector is planned for OpenAgent v0.2")
