import warnings
from ._cosmos_regions import CosmosRegion


def _adjust_preferred_locations(
    application_region: CosmosRegion | str | None,
    regions_by_latency: list[CosmosRegion],
) -> list[CosmosRegion]:
    """
    Return a reordered copy of ``regions_by_latency`` suitable for ``ConnectionPolicy.PreferredLocations``.  
    If ``application_region`` is valid it is prepended to the list; otherwise the original ordering is
    returned unchanged.

    :param CosmosRegion | str | None application_region: Azure region where the application 
        is running, e.g. ``"East US"`` or ``CosmosRegion.EAST_US``.
    :param list[CosmosRegion] regions_by_latency: Regions configured on the Cosmos DB account,
        sorted in ascending order of round-trip latency.
    :returns: Copy of ``regions_by_latency`` with ``application_region`` first when applicable.
    :rtype: list[CosmosRegion]
    """
    regions_by_latency = list(regions_by_latency) # make a copy

    if not application_region:
        return regions_by_latency

    try:
        application_region = CosmosRegion(application_region)
    except ValueError:
        warnings.warn(
            f"Specified 'application_region' '{application_region}' is not a valid Azure region. "
            f"The nearest region as measured by latency is '{regions_by_latency[0]}' and "
            f"it will be used to serve read requests.",
            UserWarning
        )
        return regions_by_latency

    if application_region not in regions_by_latency:
        warnings.warn(
            f"'application_region' is set to '{application_region}', but the region is not "
            f"configured on the account. The nearest region as measured by latency is "
            f"'{regions_by_latency[0]}' and it will be used to serve read requests. If you "
            f"add '{application_region}' to the account in the future, it will be used "
            f"to serve reads instead.",
            UserWarning
        )
        regions_by_latency.insert(0, application_region)

    elif application_region != regions_by_latency[0]:
        warnings.warn(
            f"'application_region' is set to '{application_region}', but the nearest "
            f"region as measured by latency is '{regions_by_latency[0]}'. "
            f"If you intentionally chose a more distant region you can ignore this "
            f"warning; otherwise consider switching to the closer region to improve performance.",
            UserWarning
        )
        regions_by_latency.remove(application_region)
        regions_by_latency.insert(0, application_region)

    return regions_by_latency