import uuid
from .uuid_alias import generate_unique_alias_id

def bill_identity_provider():
    bill_id = str(uuid.uuid4())
    alias = generate_unique_alias_id()
    return bill_id, alias
