# Replace ENDPOINT, ACCOUNT_KEY and REGIONS with values from your Azure Cosmos DB account.
class Configurations(object):
    ENDPOINT = "ENDPOINT"
    ACCOUNT_KEY = "MASTER_KEY"
    REGIONS = "REGIONS"
    DATABASE_NAME = "multimaster_demo_db"
    BASIC_COLLECTION_NAME = "basic_coll"
    MANUAL_COLLECTION_NAME = "manual_coll"
    LWW_COLLECTION_NAME = "lww_coll"
    UDP_COLLECTION_NAME = "udp_coll"
