import streamlit as st
import openai

# Set your OpenAI API Key here
OPENAI_API_KEY = "YOUR_OPEN_API_KEY"
openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="🏋️‍♂️ Fitness Assistant", page_icon="💪", layout="centered")

# Styling and Title
st.markdown("<h1 style='text-align: center;'>🏋️‍♂️ Fitness Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>💪 Get a personalized 120-day fitness plan!</p>", unsafe_allow_html=True)

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "👋 Welcome! Let's create your personalized 120-day fitness plan. Tell me about yourself!"}
    ]

if "weight_question_id" not in st.session_state:
    st.session_state.weight_question_id = False  # Unique flag for weight input tracking

if "plan_finalized" not in st.session_state:
    st.session_state.plan_finalized = False  # Track if plan is finalized

# Function to generate a response using OpenAI's GPT-4
def get_openai_response(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """
                You are a **fitness chatbot** that creates a **customized 120-day fitness plan**. 
                
                **Rules:**
                - If the user asks anything **not related to fitness**, respond with "I'm a fitness chatbot, and I can only help with fitness-related queries."
                - Gather information interactively by asking:
                  1. "What is your weight? (kg/lbs)" (This should track weight_question_id)
                  2. "What is your height? (cm)"
                  3. "Do you have any injuries? (Yes/No, if yes, specify)"
                  4. "What is your fitness goal? (Muscle Gain, Weight Loss, Endurance, General Fitness)"
                  5. "How many days per week will you train? (1-7)" (Should not trigger weight validation)
                  6. "What type of meal plan do you follow? (Vegetarian, Vegan, Keto, Balanced, High Protein, Low Carb)"
                  7. "What is your experience level? (Beginner, Intermediate, Advanced)"
                
                - **Only for the weight question**, if the user provides only a number (e.g., 90, 185), ask them to specify kg or lbs before proceeding.
                - **Do NOT apply this check to other numeric inputs like 'days per week'**.
                - **Stick to 120-days**.
                - Once all details are collected, generate a **120-day fitness plan**.
                - **After finalizing the fitness plan, do NOT respond to any non-fitness-related queries. Simply ignore them.**
                """},
            ] + messages
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating response: {str(e)}"
 
# Sidebar for mode selection
with st.sidebar:
    st.markdown("### Latest Updates:")
    st.write("Check out the latest features and updates in fitness trends!")
    st.write("https://www.sciencedaily.com/news/health_medicine/fitness/")
# Main chat interface

# Main chat interface
st.markdown("### Chat with Fitness Assistant")

# Chat input box for user messages
user_input = st.chat_input("Your message")

# Process user input
if user_input:
    if st.session_state.weight_question_id:
        # If weight was pending and user now specifies kg/lbs, accept the input
        if any(unit in user_input.lower() for unit in ["kg", "lbs"]):
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.weight_question_id = False  # Reset weight flag
            response = get_openai_response(st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        else:
            # If user still hasn't specified kg/lbs, remind them again
            st.session_state.chat_history.append({"role": "assistant", "content": "Please specify whether your weight is in kg or lbs (e.g., 90kg or 185lbs)."})
    elif "What is your weight?" in st.session_state.chat_history[-1]["content"]:
        # If the last question was about weight and user gave only a number, prompt for unit
        if user_input.isdigit() or (user_input.replace('.', '', 1).isdigit() and user_input.count('.') <= 1):
            st.session_state.chat_history.append({"role": "assistant", "content": "Please specify whether your weight is in kg or lbs (e.g., 90kg or 185lbs)."})
            st.session_state.weight_question_id = True  # Set weight tracking flag
        else:
            # Continue normally if the user provides valid input with unit
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            response = get_openai_response(st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
    else:
        # Prevents weight validation from interfering with other numerical inputs
        if "How many days per week will you train?" in st.session_state.chat_history[-1]["content"]:
            if user_input.isdigit() and 1 <= int(user_input) <= 7:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                response = get_openai_response(st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            else:
                st.session_state.chat_history.append({"role": "assistant", "content": "Please enter a number between 1 and 7 for training days."})
        else:
            # Normal processing before the plan is finalized
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            response = get_openai_response(st.session_state.chat_history)

            # Check if the response contains final fitness plan indicators
            if "Day 120" in response or "finalized" in response.lower():
                st.session_state.plan_finalized = True  # Mark the plan as finalized

            st.session_state.chat_history.append({"role": "assistant", "content": response})

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
