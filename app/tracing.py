import os
from langfuse import get_client

langfuse = get_client()

print("LANGFUSE_PUBLIC_KEY:", os.getenv("LANGFUSE_PUBLIC_KEY"))
print("LANGFUSE_HOST:", os.getenv("LANGFUSE_HOST"))