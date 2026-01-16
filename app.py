import streamlit as st
from transformers import pipeline
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Emotion-Aware GenAI Mentor",
    page_icon="🎓",
    layout="centered"
)

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    return pipeline("text2text-generation", model="google/flan-t5-base")

llm = load_model()

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "welcome"

if "progress" not in st.session_state:
    st.session_state.progress = {
        "attempts": 0,
        "confused": 0,
        "stressed": 0,
        "confident": 0,
        "normal": 0
    }

if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""

# ---------------- UI THEME ----------------
def set_background(color):
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {color};
        }}
        .title {{
            text-align: center;
            font-size: 42px;
            font-weight: 800;
            color: #1f2d3d;
        }}
        .subtitle {{
            text-align: center;
            font-size: 18px;
            color: #2c3e50;
        }}
        .tag {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            background: #111827;
            color: white;
            font-size: 12px;
            margin-right: 8px;
        }}
        .small {{
            font-size: 14px;
            color: #4b5563;
        }}
    </style>
    """, unsafe_allow_html=True)

# ---------------- EMOTION DETECTION ----------------
def detect_emotion(text: str):
    t = text.lower()

    confused = ["confuse", "don't understand", "cannot understand", "doubt", "help", "stuck", "hard", "difficult"]
    stressed = ["stress", "panic", "tension", "scared", "worried", "anxiety", "exam pressure"]
    confident = ["easy", "i know", "understood", "simple", "clear", "got it", "quickly"]

    if any(k in t for k in stressed):
        return "stressed"
    if any(k in t for k in confused):
        return "confused"
    if any(k in t for k in confident):
        return "confident"
    return "normal"

# ---------------- BETTER GENERATION (NO REPETITION) ----------------
def generate_answer(prompt: str, max_tokens=220):
    out = llm(
        prompt,
        max_new_tokens=max_tokens,
        do_sample=False,              # ✅ stop random repetition
        num_beams=4,                  # ✅ better quality
        repetition_penalty=2.0,       # ✅ reduces repeated phrases
        no_repeat_ngram_size=3        # ✅ blocks repeated n-grams
    )
    return out[0]["generated_text"].strip()

# ---------------- PAGE 1: WELCOME ----------------
if st.session_state.page == "welcome":
    set_background("#f8f6f0")

    st.markdown("<div class='title'>🎓 Emotion-Aware GenAI Mentor</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Personalized learning + emotional support (prototype)</div><br>", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;">
        <span class="tag">Emotion Detection</span>
        <span class="tag">Adaptive Learning</span>
        <span class="tag">Quiz Generator</span>
        <span class="tag">Study Planner</span>
    </div>
    <br>
    """, unsafe_allow_html=True)

    st.markdown("### 👋 Welcome Student!")
    st.write("This mentor explains concepts and adapts teaching based on student emotion.")
    st.info("✅ Confused → slow step-by-step\n\n✅ Stressed → calm supportive\n\n✅ Confident → advanced & fast")

    if st.button("🚀 Start Learning"):
        st.session_state.page = "mentor"
        st.rerun()

# ---------------- PAGE 2: MENTOR DASHBOARD ----------------
elif st.session_state.page == "mentor":
    set_background("#fff5ee")

    st.markdown("<div class='title'>🧠 Academic Mentor Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Ask doubts • Adaptive answers • Quiz • Study Plan</div><br>", unsafe_allow_html=True)

    with st.sidebar:
        st.header("📌 Menu")
        mode = st.radio("Choose Feature:", ["Ask Mentor", "Generate Quiz", "Create Study Plan", "Progress Dashboard"])
        st.divider()
        if st.button("🏠 Back to Home"):
            st.session_state.page = "welcome"
            st.rerun()

    # ---------------- ASK MENTOR ----------------
    if mode == "Ask Mentor":
        st.subheader("✍️ Ask Your Question")
        question = st.text_input("Enter your topic/question:")

        if st.button("📘 Get Mentor Explanation"):
            if question.strip() == "":
                st.error("❌ Please enter a question.")
            else:
                st.session_state.progress["attempts"] += 1
                emotion = detect_emotion(question)

                # Emotion + prompt
                if emotion == "confused":
                    st.session_state.progress["confused"] += 1
                    st.warning("😟 Detected Emotion: Confused")
                    teaching_mode = "SLOW + Step-by-step"
                    prompt = f"""
You are an expert teacher.
Student is CONFUSED.
Explain very slowly using very simple words.
Use step-by-step explanation and 1 easy example.
Do not repeat sentences.

Answer format:
1) Definition
2) Step-by-step explanation
3) Example
4) Summary

Question: {question}
"""
                elif emotion == "stressed":
                    st.session_state.progress["stressed"] += 1
                    st.warning("😫 Detected Emotion: Stressed")
                    teaching_mode = "CALM + Supportive"
                    prompt = f"""
You are an expert teacher.
Student is STRESSED.
Be calm, supportive and motivating.
Use short sentences.
Do not repeat sentences.

Answer format:
1) Simple explanation
2) Easy example
3) Motivation line

Question: {question}
"""
                elif emotion == "confident":
                    st.session_state.progress["confident"] += 1
                    st.success("🙂 Detected Emotion: Confident")
                    teaching_mode = "FAST + Advanced"
                    prompt = f"""
You are an expert mentor.
Student is CONFIDENT.
Explain quickly and clearly.
Add 1 advanced insight + 1 real-world application.
Do not repeat sentences.

Answer format:
1) Quick explanation
2) Advanced insight
3) Real-world application
4) Challenge question

Question: {question}
"""
                else:
                    st.session_state.progress["normal"] += 1
                    st.info("😐 Detected Emotion: Normal")
                    teaching_mode = "NORMAL"
                    prompt = f"""
You are a friendly academic mentor.
Explain clearly in simple words.
Do not repeat sentences.

Answer format:
1) Definition
2) Explanation
3) 2 examples
4) Quick summary

Question: {question}
"""

                st.caption(f"📌 Teaching Mode: {teaching_mode}")

                with st.spinner("Mentor is thinking... 🤖"):
                    time.sleep(0.5)
                    answer = generate_answer(prompt, max_tokens=260)

                st.success("✅ Mentor Explanation")
                st.write(answer)
                st.session_state.last_topic = question

    # ---------------- QUIZ GENERATOR ----------------
    elif mode == "Generate Quiz":
        st.subheader("📝 Quiz Generator")
        topic = st.text_input("Topic for quiz:", value=st.session_state.last_topic)
        level = st.selectbox("Difficulty Level:", ["Easy", "Medium", "Hard"])

        if st.button("🎯 Generate Quiz"):
            if topic.strip() == "":
                st.error("❌ Please enter a topic.")
            else:
                prompt = f"""
Create 5 {level} quiz questions on: {topic}
Do not repeat sentences.

Format:
Q1) ...
A1) ...
Q2) ...
A2) ...
Add 1 line explanation for each answer.
"""
                with st.spinner("Generating quiz..."):
                    quiz = generate_answer(prompt, max_tokens=300)
                st.success("✅ Quiz Generated")
                st.write(quiz)

    # ---------------- STUDY PLAN ----------------
    elif mode == "Create Study Plan":
        st.subheader("📅 Personalized Study Plan")
        topic = st.text_input("Topic:", value=st.session_state.last_topic)
        days = st.slider("Number of days:", 3, 30, 7)
        time_per_day = st.selectbox("Daily study time:", ["30 mins", "1 hour", "2 hours", "3 hours"])

        if st.button("📌 Create Study Plan"):
            if topic.strip() == "":
                st.error("❌ Please enter a topic.")
            else:
                prompt = f"""
Create a {days}-day study plan for: {topic}
Daily time: {time_per_day}
Do not repeat sentences.

Give day-wise:
- Topics
- Tasks
- Practice
Include revision day.
"""
                with st.spinner("Creating plan..."):
                    plan = generate_answer(prompt, max_tokens=320)
                st.success("✅ Study Plan Ready")
                st.write(plan)

    # ---------------- PROGRESS DASHBOARD ----------------
    elif mode == "Progress Dashboard":
        st.subheader("📊 Progress Dashboard")
        p = st.session_state.progress

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Questions", p["attempts"])
            st.metric("Confused Sessions", p["confused"])
            st.metric("Stressed Sessions", p["stressed"])
        with col2:
            st.metric("Confident Sessions", p["confident"])
            st.metric("Normal Sessions", p["normal"])

        st.info("This prototype tracks emotions and adapts teaching style accordingly.")
