from desc_globus_flow.flow_management import UUID_DB

# USDF
UUID_DB.set("31f8393f-79ef-4da4-a395-7127edd9b3a4", "collections",
            {"site": "USDF", "collection": "slac#s3df_globus5"})
UUID_DB.set("ac73ee3a-3f2e-425c-b618-f0079c953e4f", "endpoints",
            {"site": "USDF", "endpoint": "lsst_desc_endpoint"})

# NERSC
UUID_DB.set("6bdc7956-fc0f-4ad2-989c-7aa5ee643a79", "collections",
            {"site": "NERSC", "collection": "NERSC Perlmutter"})
UUID_DB.set("54183796-65d2-4d85-bffd-044a6c237345", "endpoints",
            {"site": "NERSC", "endpoint": "lsst_desc_endpoint"})

# ALCF
UUID_DB.set("9032dd3a-e841-4687-a163-2720da731b5b", "collections",
            {"site": "ALCF", "collection": "alcf#dtn_home"})
UUID_DB.set("482a78ef-df3b-41ea-8100-bd04ef868346", "endpoints",
            {"site": "ALCF", "endpoint": "lsst_desc_endpoint"})
