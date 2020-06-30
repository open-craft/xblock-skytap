"""
Exceptions for the Skytap XBlock.
"""


class BoomiConfigurationMissingError(RuntimeError):
    """
    Raised if XBLOCK_SETTINGS for Skytap XBlock do not contain "boomi_configuration" entry.
    """

class BoomiConfigurationInvalidError(RuntimeError):
    """
    Raised if "boomi_configuration" for Skytap XBlock is missing one or more relevant entries.
    """
