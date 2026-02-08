import os
import random
import re
from datetime import datetime

import pandas as pd
import streamlit as st
from rapidfuzz import fuzz

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "quotes.csv")

DEFAULT_TAGS = [
    "independence","love_vs_autonomy","identity","morality_religion",
    "class_power","gender","voice_narration","gothic","education_growth"
]

def ensure_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        pd.DataFrame(columns=["quote","speaker","chapter","page","themes","context"]).to_csv(CSV_PATH, index=False)

def normalize(s):
    return re.sub(r"\s+"," ",(s or "").lower().strip())

def similarity(a,b):
    return fuzz.token_set_ratio(normalize(a), normalize(b))

def cloze(q, frac):
    w=q.split(); n=max(2,int(len(w)*frac))
    hide=set(random.sample(range(len(w)),min(n,len(w))))
    return " ".join("____" if i in hide else x for i,x in enumerate(w))

def load():
    ensure_data()
    return pd.read_csv(CSV_PATH).fillna("")

def save(df):
    df.to_csv(CSV_PATH,index=False)

def teel(text):
    t=text.lower()
    return {
        "Topic sentence": "OK" if len(text)>25 else "Needs clearer topic sentence",
        "Evidence": "OK" if '"' in text else "Embed a short quote",
        "Analysis": "OK" if any(w in t for w in ["suggests","reveals","implies"]) else "Add analysis verbs",
        "Complexity": "OK" if any(w in t for w in ["however","yet","but"]) else "Add complexity (however/yet)",
    }

st.set_page_config(page_title="Jane Eyre VCE Tutor",layout="wide")
st.title("📚 Jane Eyre — VCE Unit 3/4 Tutor")

df = load()

tabs = st.tabs(["Quote Trainer","Essay Coach","Quote Bank"])

with tabs[0]:
    if len(df)==0:
        st.info("Add quotes first.")
    else:
        r=df.sample(1).iloc[0]
        st.markdown(f"> {cloze(r.quote,0.4)}")
        ans=st.text_area("Type the quote:")
        if st.button("Check"):
            st.write("Similarity:", similarity(ans,r.quote))
            st.markdown(f"> {r.quote}")

with tabs[1]:
    text=st.text_area("Paste a paragraph:")
    if st.button("Feedback"):
        for k,v in teel(text).items():
            st.write(f"**{k}:** {v}")

with tabs[2]:
    q=st.text_input("Quote")
    s=st.text_input("Speaker")
    c=st.text_input("Chapter")
    p=st.text_input("Page")
    t=st.multiselect("Themes",DEFAULT_TAGS)
    ctx=st.text_input("Context")
    if st.button("Add quote"):
        new=pd.DataFrame([[q,s,c,p,"|".join(t),ctx]],columns=df.columns)
        save(pd.concat([df,new],ignore_index=True))
        st.success("Added")
        st.rerun()
