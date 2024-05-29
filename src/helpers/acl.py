from yaml import safe_load

from src.helpers.cache import acl_cache


class IsOwnStoreCondition:
    condition_name = "is_own_store"

    def __init__(self, kwargs) -> None:
        self.kwargs = kwargs

    def check(self, config):
        filters = config.get("filters", {})
        for filt in filters:
            if filt.get("field") != "store_id":
                continue
            return filt.get("value") == self.kwargs.get("store_id")
        return False  # Filter on own store is required

class ACLConditionFactory:
    ACL_CONDITIONS = [
        IsOwnStoreCondition
    ]

    @classmethod
    def get_condition(cls, condition_type):
        for condition in cls.ACL_CONDITIONS:
            if condition.condition_name == condition_type:
                return condition
        return None


def load_acl():
    """Loads the ACL configuration from the acl.yml file"""
    with open('./src/static/acl.yaml') as f:
        data = safe_load(f)
        for role in data:
            acl_cache.set(role, data[role])
    

def _get_report_type_access(role, report_type) -> dict:
    """Returns the config of report that the user is allowed to request"""
    data, hit = acl_cache.get(role)
    if not hit:
        load_acl()
        data, _ = acl_cache.get(role)

    return data.get(report_type, [])


def _check_conditions(allowed_config, config, **kwargs):
    for filter_config in allowed_config.get("filters", {}).values():
        conditions = (filter_config or {}).get("conditions")

        for condition in conditions or []:
            condition_klass = ACLConditionFactory.get_condition(condition)
            if not condition_klass:
                raise RuntimeError("Invalid condition type, check acl config")
            inst = condition_klass(kwargs)
            if not inst.check(config):
                return False
    return True

def has_permission(role, report_type, config, **kwargs) -> bool:
    """Compares the given config with the allowed config for the given role and report type."""
    allowed_config = _get_report_type_access(role, report_type)
    if not allowed_config:
        return False

    metrics_allowed = set(config.get("metrics", [])) <= set(allowed_config.get("metrics", []))
    dimensions_allowed = set(config.get("dimensions", [])) <= set(allowed_config.get("dimensions", []))

    requested_filters = {filt.get("field") for filt in config.get("filters", [])}
    filters_allowed = requested_filters <= set(allowed_config.get("filters", {}).keys())

    return (
        metrics_allowed 
        and dimensions_allowed 
        and filters_allowed 
        and _check_conditions(allowed_config, config, **kwargs)
    )
