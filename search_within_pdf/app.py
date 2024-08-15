import streamlit as st
from authentication import create_user, verify_user, get_user_password, update_user_password
from captcha_utils import generate_captcha_code, generate_captcha_image
from image_processing import extract_text_from_image
from pdf_utils import find_text_in_pdf
import io

# Streamlit App with Built-In Theme Management
st.set_page_config(page_title="Text Extraction and PDF Search", layout="wide")

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'current_page' not in st.session_state:
    st.session_state.current_page = "main"

if 'captcha_code' not in st.session_state:
    st.session_state.captcha_code = None
    st.session_state.captcha_image = None

if 'reset_email' not in st.session_state:
    st.session_state.reset_email = None

# Handle query parameters for page navigation
query_params = st.query_params
if 'page' in query_params:
    st.session_state.current_page = query_params['page'][0]

# Header with fixed position
st.markdown("""
<style>
    .header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #4CAF50;
        color: white;
        text-align: left;
        padding: 10px;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
    }
    .header-left {
        font-size: 24px;
    }
    .header-right a {
        color: white;
        padding: 0 15px;
        text-decoration: none;
        font-size: 18px;
    }
    .logout-button {
        background-color: #f44336;
        color: white;
        border: none;
        padding: 10px;
        cursor: pointer;
    }
    .main-content {
        margin-top: 100px; /* Adjusted to ensure header visibility */
    }
</style>
<div class="header">
    <div class="header-left">
        <img src="https://via.placeholder.com/50" alt="Logo" style="vertical-align: middle;">
        <span style="vertical-align: middle;">SearchWithinPDF</span>
    </div>
    <div class="header-right">
        {% if st.session_state.authenticated %}
            <button class="logout-button" onclick="window.location.href='?page=logout'">Logout</button>
        {% else %}
            <a href="?page=signup">Sign Up</a>
            <a href="?page=login">Login</a>
        {% endif %}
    </div>
</div>
<div class="main-content">
""", unsafe_allow_html=True)

# Logout page
if st.session_state.current_page == "logout":
    st.session_state.authenticated = False
    st.session_state.current_page = "main"
    st.success("You have been logged out.")

# Sign-up page
elif st.session_state.current_page == "signup":
    st.title("Sign Up")
    name = st.text_input("Name")
    surname = st.text_input("Surname")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password == confirm_password:
            create_user(email, password, name, surname)
            st.success("Account created successfully! Please log in.")
            st.session_state.current_page = "login"
        else:
            st.error("Passwords do not match!")
    
    st.write("Already have an account?")
    if st.button("Go to Login"):
        st.session_state.current_page = "login"

# Login page
elif st.session_state.current_page == "login":
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify_user(email, password):
            st.session_state.authenticated = True
            st.success("Login successful!")
            st.session_state.current_page = "main"
        else:
            st.error("Invalid email or password.")

    st.write("Don't have an account?")
    if st.button("Go to Sign Up"):
        st.session_state.current_page = "signup"

    st.write("Forgot your password?")
    if st.button("Forgot Password"):
        if get_user_password(email):
            st.session_state.reset_email = email
            st.session_state.captcha_code = generate_captcha_code()
            st.session_state.captcha_image = generate_captcha_image(st.session_state.captcha_code)
            st.session_state.current_page = "verify_captcha"
        else:
            st.error("Email not found!")

# CAPTCHA Verification Page
elif st.session_state.current_page == "verify_captcha":
    st.title("Verify CAPTCHA")
    if st.session_state.captcha_image:
        st.image(st.session_state.captcha_image, caption='CAPTCHA', use_column_width=False)  # Adjust size
    captcha_input = st.text_input("Enter CAPTCHA Code")
    
    if st.button("Submit"):
        if captcha_input == st.session_state.captcha_code:
            st.session_state.current_page = "reset_password"
        else:
            st.error("Incorrect CAPTCHA code. Please try again.")
    
    if st.button("Refresh CAPTCHA"):
        st.session_state.captcha_code = generate_captcha_code()
        st.session_state.captcha_image = generate_captcha_image(st.session_state.captcha_code)
        st.write("CAPTCHA refreshed!")

# Reset Password Page
elif st.session_state.current_page == "reset_password":
    st.title("Reset Password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")
    
    if st.button("Reset Password"):
        if new_password == confirm_password:
            if st.session_state.reset_email:
                update_user_password(st.session_state.reset_email, new_password)
                st.success("Password has been reset successfully.")
                st.session_state.current_page = "login"
            else:
                st.error("No email address found.")
        else:
            st.error("Passwords do not match!")

# Main page
elif st.session_state.current_page == "main":
    st.markdown("<h1 style='text-align: center;'>Text Extraction and Search in PDF</h1>", unsafe_allow_html=True)

    search_method = st.radio(
        "Select the search method:",
        ("Extract from Image", "Manual Entry"),
        index=0
    )

    if search_method == "Extract from Image":
        st.write("Upload an image to extract text and then upload a PDF to search for this text.")
        
        image_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"], key="image_upload")
        pdf_file = st.file_uploader("Upload a PDF", type="pdf", key="pdf_upload")

    elif search_method == "Manual Entry":
        st.write("Type the text you want to find, then upload a PDF to search for this text.")
        
        manual_text = st.text_input("Type the text you want to find:", "", key="text_input")
        pdf_file = st.file_uploader("Upload a PDF", type="pdf", key="pdf_upload")

    st.markdown("""
    <style>
        .stButton > button {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 200px;
            font-size: 18px;
            padding: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    if st.button("Find", key="find"):
        if not st.session_state.authenticated:
            st.warning("Please log in to use the Find feature.")
            st.session_state.current_page = "login"
        else:
            if search_method == "Extract from Image":
                if image_file and pdf_file:
                    with open("uploaded_image.png", "wb") as f:
                        f.write(image_file.getbuffer())
                    search_text = extract_text_from_image("uploaded_image.png")
                    
                    with open("uploaded_pdf.pdf", "wb") as f:
                        f.write(pdf_file.getbuffer())
                    locations = find_text_in_pdf("uploaded_pdf.pdf", search_text)

                    if locations:
                        page_numbers = [str(loc['page']) for loc in locations]
                        st.subheader("Page Numbers where Text was Found:")
                        st.write(f"<div style='text-align: center; font-size: 20px;'><b>{', '.join(page_numbers)}</b></div>", unsafe_allow_html=True)
                    else:
                        st.subheader("No matches found.")
                elif not image_file:
                    st.write("Please upload an image to extract text.")
                elif not pdf_file:
                    st.write("Please upload a PDF to search the text.")
                else:
                    st.write("Please upload both an image and a PDF to proceed.")

            elif search_method == "Manual Entry":
                if pdf_file and manual_text:
                    with open("uploaded_pdf.pdf", "wb") as f:
                        f.write(pdf_file.getbuffer())
                    locations = find_text_in_pdf("uploaded_pdf.pdf", manual_text)

                    if locations:
                        page_numbers = [str(loc['page']) for loc in locations]
                        st.subheader("Page Numbers where Text was Found:")
                        st.write(f"<div style='text-align: center; font-size: 20px;'><b>{', '.join(page_numbers)}</b></div>", unsafe_allow_html=True)
                    else:
                        st.subheader("No matches found.")
                elif not pdf_file:
                    st.write("Please upload a PDF to search the text.")
                elif not manual_text:
                    st.write("Please enter the text you want to find.")
                else:
                    st.write("Please upload a PDF and enter the text to search directly.")
