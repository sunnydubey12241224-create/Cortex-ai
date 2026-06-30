import warnings
warnings.filterwarnings("ignore")

from transformers import pipeline

from transformers import pipeline

summarizer = pipeline("text2text-generation", model="google/flan-t5-small")

def summarize_text(text):
    prompt = "Summarize this email:\n" + text
    result = summarizer(prompt, max_length=100, do_sample=False)
    return result[0]["generated_text"]

def summarize_text(text):
    summary = summarizer(text[:1000], max_length=100, min_length=30)
    return summary[0]["summary_text"]