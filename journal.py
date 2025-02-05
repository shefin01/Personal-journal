import streamlit as st
import os
import json
import hashlib
from datetime import datetime

# File paths
USER_FILE = "user.json"
JOURNAL_FILE = "journal_entries.json"


def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    """Load users from JSON file."""
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as file:
            return json.load(file)
    return {}


def save_users(users):
    """Save users to JSON file."""
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)


def load_journal():
    """Load journal entries from JSON file."""
    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, "r") as file:
            return json.load(file)
    return []


def save_journal(entries):
    """Save journal entries to JSON file."""
    with open(JOURNAL_FILE, "w") as file:
        json.dump(entries, file, indent=4)


def add_entry(username, title, content):
    """Adds a new journal entry."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entries = load_journal()
    entries.append({"username": username, "title": title, "content": content, "timestamp": timestamp})
    save_journal(entries)
    st.success("✅ Entry added successfully!")


def view_entries(username):
    """Displays user's journal entries."""
    entries = load_journal()
    return [entry for entry in entries if entry["username"] == username]


def search_entries(username, keyword):
    """Search for journal entries by keyword."""
    keyword = keyword.lower()
    return [entry for entry in view_entries(username) if keyword in entry["content"].lower()]


def delete_entry(username, entry_index):
    """Deletes a journal entry."""
    entries = load_journal()
    user_entries = view_entries(username)

    if 0 <= entry_index < len(user_entries):
        entries.remove(user_entries[entry_index])
        save_journal(entries)
        st.success("✅ Entry deleted successfully!")


# ---- Streamlit UI ----

st.title("📓 Personal Journal App")

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "show_signup" not in st.session_state:
    st.session_state["show_signup"] = False


# Logout Function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.success("✅ Logged out successfully!")
    st.rerun()


# Authentication UI
if not st.session_state["logged_in"]:
    st.sidebar.title("🔐 Login or Sign Up")

    if not st.session_state["show_signup"]:
        # Login Form
        st.sidebar.subheader("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Login"):
            users = load_users()
            if username in users and users[username] == hash_password(password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.sidebar.success(f"✅ Welcome, {username}!")
                st.rerun()
            else:
                st.sidebar.error("❌ Invalid username or password.")

        st.sidebar.markdown("---")
        if st.sidebar.button("Create an Account"):
            st.session_state["show_signup"] = True
            st.rerun()

    else:
        # Signup Form
        st.sidebar.subheader("🆕 Create Account")
        new_username = st.sidebar.text_input("New Username")
        new_password = st.sidebar.text_input("New Password", type="password")
        confirm_password = st.sidebar.text_input("Confirm Password", type="password")

        if st.sidebar.button("Sign Up"):
            users = load_users()
            if new_username in users:
                st.sidebar.error("❌ Username already exists.")
            elif new_password != confirm_password:
                st.sidebar.error("❌ Passwords do not match.")
            else:
                users[new_username] = hash_password(new_password)
                save_users(users)
                st.sidebar.success("✅ Account created! Please log in.")
                st.session_state["show_signup"] = False
                st.rerun()

        st.sidebar.markdown("---")
        if st.sidebar.button("Back to Login"):
            st.session_state["show_signup"] = False
            st.rerun()

# ---- Main Dashboard ----
else:
    st.sidebar.title(f"👤 Welcome, {st.session_state['username']}!")
    st.sidebar.button("Logout", on_click=logout)

    # Tabbed Navigation
    tab = st.radio("📌 Choose an option:", ["📖 View Entries", "📝 Add Entry", "🔍 Search", "❌ Delete Entry"])

    if tab == "📝 Add Entry":
        st.subheader("📝 Add a New Journal Entry")
        title = st.text_input("Title")
        content = st.text_area("Write your journal entry here...")

        if st.button("Save Entry"):
            if title and content:
                add_entry(st.session_state["username"], title, content)
                st.rerun()
            else:
                st.warning("⚠️ Title and content cannot be empty.")

    elif tab == "📖 View Entries":
        st.subheader("📖 Your Journal Entries")
        entries = view_entries(st.session_state["username"])

        if entries:
            for i, entry in enumerate(entries):
                st.markdown(f"**{i + 1}. {entry['title']}** ({entry['timestamp']})")
                st.write(entry["content"])
                st.markdown("---")
        else:
            st.info("No entries found. Start by adding a new entry.")

    elif tab == "🔍 Search":
        st.subheader("🔍 Search Journal Entries")
        keyword = st.text_input("Enter a keyword")

        if st.button("Search"):
            results = search_entries(st.session_state["username"], keyword)
            if results:
                for i, entry in enumerate(results):
                    st.markdown(f"**{i + 1}. {entry['title']}** ({entry['timestamp']})")
                    st.write(entry["content"])
                    st.markdown("---")
            else:
                st.warning("No matching entries found.")

    elif tab == "❌ Delete Entry":
        st.subheader("❌ Delete a Journal Entry")
        entries = view_entries(st.session_state["username"])

        if entries:
            entry_titles = [f"{i + 1}. {entry['title']}" for i, entry in enumerate(entries)]
            selected_entry = st.selectbox("Select an entry to delete", entry_titles)

            if st.button("Delete Entry"):
                entry_index = entry_titles.index(selected_entry)
                delete_entry(st.session_state["username"], entry_index)
                st.rerun()
        else:
            st.warning("No entries to delete.")
