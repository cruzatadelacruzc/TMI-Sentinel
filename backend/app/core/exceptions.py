class DataSourceError(Exception):
    """Base error for external data-source failures."""


class ProviderError(DataSourceError):
    """Raised when an external rate provider cannot return usable data."""


class CalculationError(Exception):
    """Base error for analytical calculation failures."""


class MissingRateHistory(CalculationError):
    """Raised when an analysis has too few observations to be meaningful."""


class ConfigurationError(Exception):
    """Raised when required application configuration is missing or invalid."""