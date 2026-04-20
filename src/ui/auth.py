"""Auth: Google Sign-In via redirect (persistent) or Guest (session-only)."""
import uuid
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session

from src.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, OAUTH_REDIRECT_URI

_AUTH_URL     = "https://accounts.google.com/o/oauth2/auth"
_TOKEN_URL    = "https://oauth2.googleapis.com/token"
_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def require_login() -> str:
    """Returns user_id. Handles OAuth callback, then shows landing if not authed."""
    _handle_oauth_callback()
    if "user_id" in st.session_state and "is_guest" in st.session_state:
        return st.session_state.user_id
    _render_landing()
    st.stop()


def _handle_oauth_callback() -> None:
    """Exchange OAuth code for user info if Google redirected back here."""
    params = st.query_params
    if "code" not in params:
        return
    try:
        oauth = OAuth2Session(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            redirect_uri=OAUTH_REDIRECT_URI,
        )
        oauth.fetch_token(_TOKEN_URL, code=params["code"])
        user_info = oauth.get(_USERINFO_URL).json()
        st.session_state.user_id    = user_info["sub"]
        st.session_state.is_guest   = False
        st.session_state.user_email = user_info.get("email", "")
        st.session_state.user_name  = user_info.get("name", "")
    except Exception as e:
        st.error(f"Sign-in failed — please try again. ({e})")
    finally:
        st.query_params.clear()
        st.rerun()


def _google_auth_url() -> str:
    oauth = OAuth2Session(
        client_id=GOOGLE_CLIENT_ID,
        redirect_uri=OAUTH_REDIRECT_URI,
        scope="openid email profile",
    )
    url, _ = oauth.create_authorization_url(_AUTH_URL, access_type="offline")
    return url


def _render_landing() -> None:
    st.markdown(
        """
        <div style='text-align:center; padding: 3rem 1rem 1.5rem;'>
            <h1 style='font-size:2.2rem; font-weight:800; margin-bottom:0.3rem;'>
                🚀 PitchBuddy
            </h1>
            <p style='color:#64748B; font-size:1.05rem; margin-bottom:2rem;'>
                Practice your startup pitch with an AI-powered VC.<br>
                Get challenged, get sharp, get funded.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_mid, col_r = st.columns([1, 2, 1])
    with col_mid:
        st.link_button(
            "Sign in with Google",
            _google_auth_url(),
            use_container_width=True,
        )

        st.markdown(
            "<div style='text-align:center; color:#94A3B8; font-size:0.8rem;"
            " margin: 8px 0;'>or</div>",
            unsafe_allow_html=True,
        )

        if st.button("Continue as Guest", use_container_width=True):
            st.session_state.user_id  = str(uuid.uuid4())
            st.session_state.is_guest = True
            st.rerun()

        st.markdown(
            "<div style='text-align:center; color:#94A3B8; font-size:0.72rem;"
            " margin-top:10px;'>Guest sessions are not saved after the tab closes.</div>",
            unsafe_allow_html=True,
        )


def render_user_info() -> None:
    """Renders user info + sign-out in the sidebar (logged-in users only)."""
    if st.session_state.get("is_guest"):
        return

    name  = st.session_state.get("user_name", "")
    email = st.session_state.get("user_email", "")

    with st.sidebar:
        st.markdown(
            f"<div style='font-size:0.78rem; color:#0F172A; font-weight:600;"
            f" padding-bottom:2px;'>{name}</div>"
            f"<div style='font-size:0.72rem; color:#94A3B8;'>{email}</div>",
            unsafe_allow_html=True,
        )
        if st.button("Sign out", use_container_width=True):
            for key in ["user_id", "is_guest", "user_email", "user_name"]:
                st.session_state.pop(key, None)
            st.rerun()
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
