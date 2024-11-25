import streamlit as st
import requests
import json
import time
from PIL import Image


# Define API Key and Base URL
API_KEY = "taPxd2jFPxNTTEXZsGAXbRxSgylLsEKi"
API_BASE_URL = "https://oapi.tasking.ai/v1"
MODEL_ID = "X5lMtrEVvhZuirQGg3aflNOW"



# Define profession and domain hierarchies
PROFESSION_DOMAINS = {
    "Teacher": [
        "Mathematics",
        "Science",
        "English",
        "History",
        "Computer Science",
        "Primary Education",
        "Secondary Education",
        "Special Education",
        "Other"
    ],
    "Doctor": [
        "General Medicine",
        "Pediatrics",
        "Cardiology",
        "Neurology",
        "Surgery",
        "Alternative Medicine",
        "Public Health",
        "Other"
    ],
    "Engineer": [
        "Civil",
        "Mechanical",
        "Electrical",
        "Software",
        "Chemical",
        "Robotics",
        "AI/ML",
        "Environmental",
        "Other"
    ],
    "Student": [
        "Arts and Humanities",
        "Science",
        "Commerce/Business",
        "Engineering",
        "Medical",
        "Computer Science",
        "Other"
    ],
    "Other": []
}

# Streamlit interface setup
st.set_page_config(page_title="AI-Buddy Assistant", page_icon="AI-Buddy.png", layout="centered")

# Load and resize the image
img = Image.open("AI Buddy Green Logo.png")
resized_img = img.resize((400, 150))

# Display the resized image
st.image(resized_img, caption="AI-Buddy Assistant")

# Custom CSS
st.markdown("""
    <style>
        .sidebar .sidebar-content {
            font-size: 1.1rem;
            color: #333333;
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
        }
        .sidebar .sidebar-content h1 {
            font-size: 1.5rem;
            font-weight: bold;
            color: #ff4b4b;
            margin-bottom: 10px;
        }
        .sidebar .sidebar-content select, .sidebar .sidebar-content textarea, .sidebar .sidebar-content input {
            border: 2px solid #ff4b4b;
            padding: 10px;
            font-size: 1.1rem;
            margin-bottom: 10px;
            border-radius: 5px;
        }
        .sidebar .sidebar-content button {
            background-color: #ff4b4b;
            color: white;
            font-size: 1.1rem;
            padding: 8px 15px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .sidebar .sidebar-content button:hover {
            background-color: #ff6565;
        }
        .st-chat-message p {
            font-size: 1.1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar title
st.sidebar.title("Want to know how AI helps in your profession and the role of AI-Buddy?")
st.sidebar.write("Select your details below and discover the potential of AI in your career!")

# First dropdown - Profession Selection
profession = st.sidebar.selectbox(
    "Choose Your Profession",
    ["Select Profession"] + list(PROFESSION_DOMAINS.keys()),
    key="profession_selector"
)

# Initialize variables
selected_profession = None
selected_domain = None

# Handle profession selection
if profession == "Other":
    custom_profession = st.sidebar.text_input("Please specify your profession")
    if custom_profession:
        selected_profession = custom_profession
else:
    selected_profession = profession

# Domain selection (only if a profession is selected and it's not "Select Profession")
if profession and profession != "Select Profession":
    if profession == "Other":
        domain = st.sidebar.text_input("Please specify your domain")
        if domain:
            selected_domain = domain
    else:
        domain = st.sidebar.selectbox(
            "Choose Your Domain",
            ["Select Domain"] + PROFESSION_DOMAINS[profession],
            key="domain_selector"
        )
        
        if domain == "Other":
            custom_domain = st.sidebar.text_input("Please specify your domain")
            if custom_domain:
                selected_domain = custom_domain
        else:
            selected_domain = domain

# Description text area
description = st.sidebar.text_area(
    "About you (a short description)", 
    placeholder="Briefly describe your role",
    key="description"
)

# Submit button with validation
if st.sidebar.button("Submit"):
    if profession == "Select Profession":
        st.sidebar.error("Please select a profession.")
    elif profession == "Other" and not custom_profession:
        st.sidebar.error("Please specify your profession.")
    elif not selected_domain or (domain == "Select Domain"):
        st.sidebar.error("Please select or specify a domain.")
    else:
        # Format the profession details for the chat
        profession_details = f"My profession is {selected_profession} in the {selected_domain} domain"
        
        # Add input details as a message to chat history
        st.session_state.messages.append({
            "role": "user",
            "content": f"{profession_details}. Here's a bit about me: {description}. Tell me  AI-Buddy can help me."
        })
        
        # Clear the sidebar content
        st.sidebar.empty()
        st.sidebar.write("Details submitted! You can continue chatting below.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I assist you today?"}
    ]

# Function to make a request to the custom API
def get_chat_response():
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    data = {
        "model": MODEL_ID,
        "messages": st.session_state.messages
    }

    try:
        response = requests.post(f"{API_BASE_URL}/chat/completions", headers=headers, json=data)
        
        if response.status_code == 200:
            response_json = response.json()
            content = response_json["choices"][0]["message"]["content"]

            try:
                content_parsed = json.loads(content)
                return content_parsed["choices"][0]["message"]["content"]
            except json.JSONDecodeError:
                return content
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    except Exception as e:
        st.error("Re-enter the prompt")
        print(f"Error: {e}")
        return None

# Function to simulate streaming effect
def display_response_streaming(response_content):
    response_placeholder = st.empty()
    streaming_text = ""
    for char in response_content:
        streaming_text += char
        response_placeholder.write(streaming_text)
        time.sleep(0.05)

# Chat interface - User Input
if prompt := st.chat_input("Type your message"):
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display chat history and generate assistant response
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Generate assistant response if the last message is from the user
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_content = get_chat_response()
            if response_content:
                display_response_streaming(response_content)
                st.session_state.messages.append({"role": "assistant", "content": response_content})
            else:
                st.write("Sorry, Re-enter the prompt")