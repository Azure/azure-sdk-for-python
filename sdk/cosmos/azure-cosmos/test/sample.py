from azure.cosmos.cosmos_client import CosmosClient
c = CosmosClient("https://java-async-gated.documents-staging.windows-ppe.net:443/", {'masterKey': "LyiYjQopDScUDPLeN6Myn4umLwFoJCttLpwpf9OoIvsyroPazV83EEwb9k7N8ANqORA4QF60mtjwwwgqfm9yVg=="})
cc = c.get_database_client("mydb").get_container_client("mycoll")
doc = cc.upsert_item(body={'id': '1', 'pk': '1', 'i': 4})
print(doc)