import asyncpg

async def get_db_connection():
    return await asyncpg.connect(
        user="neondb_owner",
        password="npg_oykgI3EtzbQ9",
        host="ep-aged-block-a63cujfq-pooler.us-west-2.aws.neon.tech",
        database="neondb",
        ssl="require"
    )