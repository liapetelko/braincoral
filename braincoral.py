import streamlit as st
import datetime
def get_timestamp():
    now = datetime.datetime.now()
    timestamp = now.strftime("%d/%m/%Y %H:%M")
    return timestamp
import random
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

# if 'firebase_initialized' not in st.session_state:
#     # Check if running locally or deployed
#     if os.path.exists("brain-coral-vocab-firebase-adminsdk.json"):
#         cred_path = "brain-coral-vocab-firebase-adminsdk.json"
#     else:
#         # For local use, fallback to the original path
#         cred_path = r"C:\steil\brain-coral-vocab-firebase-adminsdk-c6g3m-b019f7d8ba.json"
    
#     if not firebase_admin._apps:
#         try:
#             cred = credentials.Certificate(cred_path)
#             firebase_admin.initialize_app(cred)
#         except Exception as e:
#             st.error(f"Error initializing Firebase: {e}")
    
#     st.session_state.firebase_initialized = True

#cred = credentials.Certificate(r"brain-coral-vocab-firebase-adminsdk-c6g3m-b019f7d8ba.json")

#if not firebase_admin._apps:
    #firebase_admin.initialize_app(cred)
#brain = firestore.client()

if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
        "universe_domain": st.secrets["firebase"].get("universe_domain", "googleapis.com")
    })
    firebase_admin.initialize_app(cred)

brain = firestore.client()

st.markdown(
    """
    <div style="text-align: center;">
        <h1>Brain Coral</h1>
    </div>
    """,
    unsafe_allow_html=True,
)
st.header("Practice words")

def get_words_from_firestore():
    words_ref = brain.collection("words").stream()
    words = []
    for word in words_ref:
        words.append(word.to_dict())
    return words
words = get_words_from_firestore()

def update_counter(word_id):
    doc_ref = brain.collection("words").document(word_id)
    doc_ref.update({"Success Counter": firebase_admin.firestore.Increment(1)})


wordsPracticeSelection = st.selectbox("Practice Options",["To English","To Hebrew"])

if "current_word" not in st.session_state:
    st.session_state.current_word = random.choice(words)

english_word = st.session_state.current_word["English"]
hebrew_word = st.session_state.current_word["Hebrew"]

if wordsPracticeSelection == "To English":
    st.subheader(hebrew_word)
    user_answer = st.text_input("Your answer:")
    correct_answer = english_word
else:  
    st.subheader(english_word)
    user_answer = st.text_input("Your answer:")
    correct_answer = hebrew_word

colbtnCheckWord, colbtnShowAnswer, colbtnNextWord = st.columns(3)

with colbtnCheckWord:
    btnCheckWord = st.button("Check ☑ ")
    if btnCheckWord:
        if user_answer:
            if user_answer.lower() == correct_answer.lower():
                st.success("Correct!")
                update_counter(english_word)
            else:
                st.error(f"Incorrect")
        else:
            st.warning("Please enter an answer.")

with colbtnShowAnswer:
    btnShowAnswer = st.button("Show Answer ✔")
    if btnShowAnswer:
        st.write(f"**{correct_answer}**")

with colbtnNextWord:
    btnNextWord = st.button("Next word ➤")
    if btnNextWord:
        st.session_state.current_word = random.choice(words)
        st.experimental_rerun()

st.markdown("---")
def add_word_to_firestore(english_word, hebrew_word):
    if english_word and hebrew_word:
        doc_ref = brain.collection("words").document(english_word)
        doc = doc_ref.get()
        if doc.exists:
            st.warning(f"Word '{english_word}' already exists!")
        else:
            doc_ref.set({
                "English": english_word,
                "Hebrew": hebrew_word,
                "English 1st Letter": english_word[0],
                "Hebrew 1st Letter": hebrew_word[0],
                "Timestamp": get_timestamp()
            })
            st.success(f"Word '{english_word}' added successfully!")
    else:
        st.error("Please fill in both English and Hebrew fields.")

st.header("Add new words")
newWordEng, newWordHeb = st.columns(2)
with newWordEng:
    newWordEnglish = st.text_input("English")
with newWordHeb:
    newWordHebrew = st.text_input("Hebrew")
btnAddNew = st.button("Add Word")
if btnAddNew:
    add_word_to_firestore(newWordEnglish, newWordHebrew)

st.subheader("Add multiple words")
words_list = st.text_area("Words list (hebrew-english structure)")
lines = words_list.strip().split('\n')

if st.button("Add Multipule Words"):
    for line in lines:
        english_word, hebrew_word = line.split('\t')
        add_word_to_firestore(hebrew_word.strip(), english_word.strip())


