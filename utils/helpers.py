from functools import wraps
import streamlit as st

def require_role(required_role):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if st.session_state.get("role") == required_role:
                return await func(*args, **kwargs)
            st.error("У вас нет прав для выполнения этого действия.")
        return wrapper
    return decorator
