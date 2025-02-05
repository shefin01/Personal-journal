import streamlit as st
import os
import json
import hashlib
from datetime import datetime
import pandas as pd

# File paths
USER_FILE = "user.json"
JOURNAL_FILE = "journal_entries.json"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as file:
            return json.load(file)
    return {}


def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)


def load_journal():
    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, "r") as file:
            return json.load(file)
    return []


def save_journal(entries):
    with open(JOURNAL_FILE, "w") as file:
        json.dump(entries, file, indent=4)


def add_entry(username, title, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entries = load_journal()
    entries.append({"username": username, "title": title, "content": content, "timestamp": timestamp})
    save_journal(entries)
    st.success("✅ Entry added successfully!")


def view_entries(username):
    entries = load_journal()
    return [entry for entry in entries if entry["username"] == username]


def search_entries(username, keyword):
    keyword = keyword.lower()
    return [entry for entry in view_entries(username) if
            keyword in entry["content"].lower() or keyword in entry["title"].lower()]


def delete_entry(username, entry_index):
    entries = load_journal()
    user_entries = view_entries(username)

    if 0 <= entry_index < len(user_entries):
        entries.remove(user_entries[entry_index])
        save_journal(entries)
        st.success("✅ Entry deleted successfully!")


def delete_account(username):
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)

    all_entries = load_journal()
    updated_entries = [e for e in all_entries if e["username"] != username]
    save_journal(updated_entries)

    st.success("✅ Account deleted successfully!")
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.rerun()


# Streamlit UI
st.title("📓 Personal Journal App")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "show_signup" not in st.session_state:
    st.session_state["show_signup"] = False


def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None


if not st.session_state["logged_in"]:
    st.sidebar.title("🔐 Login or Sign Up")

    if not st.session_state["show_signup"]:
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Login"):
            users = load_users()
            if username in users and users[username] == hash_password(password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.sidebar.error("❌ Invalid username or password.")

        if st.sidebar.button("Create an Account"):
            st.session_state["show_signup"] = True
            st.rerun()
    else:
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

        if st.sidebar.button("Back to Login"):
            st.session_state["show_signup"] = False
            st.rerun()

else:
    st.sidebar.title(f"👤 Welcome, {st.session_state['username']}!")
    st.sidebar.button("Logout", on_click=logout)

    tab = st.radio("📌 Choose an option:", ["📖 View Entries", "📝 Add Entry", "🔍 Search Entries", "❌ Delete Entry"])

    if tab == "📖 View Entries":
        st.subheader("📖 Your Journal Entries")
        entries = view_entries(st.session_state["username"])

        if entries:
            df = pd.DataFrame(
                [{"#": i + 1, "Title": e["title"], "Date": e["timestamp"]} for i, e in enumerate(entries)]
            )
            st.table(df)

            entry_titles = [f"{i + 1}. {entry['title']}" for i, entry in enumerate(entries)]
            selected_entry = st.selectbox("Select an entry to view", entry_titles)

            if st.button("View Entry"):
                selected_index = entry_titles.index(selected_entry)
                st.session_state["selected_entry"] = entries[selected_index]
                st.rerun()

            if "selected_entry" in st.session_state and st.session_state["selected_entry"]:
                st.subheader(f"📝 {st.session_state['selected_entry']['title']}")
                st.write(f"📅 Date: {st.session_state['selected_entry']['timestamp']}")
                st.write(st.session_state["selected_entry"]["content"])
        else:
            st.warning("⚠️ Your journal is empty. Start writing your first entry!")

    elif tab == "📝 Add Entry":
        st.subheader("📝 Add a New Journal Entry")
        title = st.text_input("Title")
        content = st.text_area("Write your journal entry here...")

        if st.button("Save Entry"):
            if title and content:
                add_entry(st.session_state["username"], title, content)
            else:
                st.warning("⚠️ Title and content cannot be empty.")

    elif tab == "🔍 Search Entries":
        st.subheader("🔍 Search Your Journal Entries")
        keyword = st.text_input("Enter a keyword to search")

        if keyword:
            entries = search_entries(st.session_state["username"], keyword)
            if entries:
                # Display search results in a table format
                df = pd.DataFrame(
                    [{"#": i + 1, "Title": e["title"], "Date": e["timestamp"]} for i, e in enumerate(entries)]
                )
                st.table(df)

                # Add option to view full entry
                entry_titles = [f"{i + 1}. {entry['title']}" for i, entry in enumerate(entries)]
                selected_entry_title = st.selectbox("Select an entry to view", entry_titles)

                if selected_entry_title:
                    selected_index = entry_titles.index(selected_entry_title)
                    selected_entry = entries[selected_index]
                    st.subheader(f"📝 {selected_entry['title']}")
                    st.write(f"📅 Date: {selected_entry['timestamp']}")
                    st.write(selected_entry["content"])

            else:
                st.warning("⚠️ No entries found with that keyword.")

    elif tab == "❌ Delete Entry":
        st.subheader("❌ Delete a Journal Entry")
        entries = view_entries(st.session_state["username"])

        if entries:
            entry_titles = [f"{i + 1}. {entry['title']}" for i, entry in enumerate(entries)]

            selected_entry = st.selectbox("Select an entry to delete", entry_titles, key="delete_select")

            if st.button("Delete Entry"):
                st.session_state["confirm_delete_entry"] = True  # Show confirmation pop-up

        else:
            st.warning("⚠️ No entries to delete.")

    # Show confirmation popup for entry deletion

    if st.session_state.get("confirm_delete_entry", False):

        st.warning("⚠️ Are you sure you want to delete this entry? This action cannot be undone.")

        col1, col2 = st.columns(2)

        with col1:

            if st.button("Yes, Delete"):
                entry_index = entry_titles.index(selected_entry)

                delete_entry(st.session_state["username"], entry_index)

                st.session_state["entry_deleted"] = True  # Success message flag

                st.session_state["confirm_delete_entry"] = False  # Hide confirmation

                st.rerun()

        with col2:

            if st.button("No, Cancel"):
                st.session_state["confirm_delete_entry"] = False  # Hide confirmation

                st.rerun()

    # Show success message after rerun

    if st.session_state.get("entry_deleted", False):

        st.success("✅ Entry deleted successfully!")

        st.session_state["entry_deleted"] = False  # Reset flag

    # Moving the delete account option to the bottom of the sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗑️ Delete Account")
    if st.sidebar.button("Delete Account"):
        st.session_state["confirm_delete_account"] = True

    if "confirm_delete_account" in st.session_state:
        st.error("⚠️ Are you sure? This will delete your account and all journal entries!")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Yes, Delete Everything"):
                delete_account(st.session_state["username"])
                del st.session_state["confirm_delete_account"]
                st.rerun()

        with col2:
            if st.button("No, Keep My Account"):
                del st.session_state["confirm_delete_account"]
