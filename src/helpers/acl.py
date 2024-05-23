from yaml import safe_load

from src.helpers.cache import acl_cache


def load_acl():
    """Loads the ACL configuration from the acl.yml file"""
    with open('./src/static/acl.yaml') as f:
        data = safe_load(f)
        for role in data:
            acl_cache.set(role, data[role])
    
def get_allowed_metrics(role, report_type) -> list:
    """Returns the list of metrics that the user is allowed to access"""
    data, hit = acl_cache.get(role)
    if not hit:
        load_acl()
        data, _ = acl_cache.get(role)

    role_configuration = data.get(role, {})
    return role_configuration.get(report_type, [])
