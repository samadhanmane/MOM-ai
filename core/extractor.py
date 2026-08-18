#Actionableitems, decision, questions
from core.summarize import split_transcript
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough,RunnableLambda

import os

def get_llm():
    return ChatMistralAI(model = "mistral-small-latest", mistral_api_key = os.getenv("MISTRAL_API_KEY"), temperature =0.3)


def build_chain(system_prompt: str) :
    llm = get_llm()
    return (
        RunnablePassthrough() | RunnableLambda(lambda x:{"text":x}) | ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human","{text}")
        ]) | llm | StrOutputParser()
    )

def run_on_chunks(transcript: str, chain, final_prompt: str) -> str:
    chunks = split_transcript(transcript)

    results = []

    for chunk in chunks:
        result = chain.invoke(chunk)
        results.append(result)

    combined_results = "\n\n".join(results)

    final_chain = build_chain(final_prompt)

    return final_chain.invoke(combined_results)

def extract_action_items(transcript:str)->str:
    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all action items. For each provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Not specified')\n\n"
        "Format as a numbered list. If none found say 'No action items found.'"
    )
    final_prompt = (
        "You are an expert meeting analyst. "
        "Below are action items extracted from multiple transcript chunks. "
        "Merge all action items into ONE final list. "
        "Remove duplicate action items, including duplicates caused by "
        "overlapping transcript chunks. "
        "Ignore 'NONE'. "
        "Do not invent any information.\n\n"
        "For each action item provide:\n"
        "- Task description\n"
        "- Owner\n"
        "- Deadline\n\n"
        "If no action items exist, say 'No action items found.' "
        "Format the final answer as a numbered list."
    )

    return run_on_chunks(transcript, chain, final_prompt)
    


def extract_key_decisions(transcript: str) -> str:
    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all key decisions made. Format as a numbered list. "
        "If none found say 'No key decisions found.'"
    )
    final_prompt = (
            "You are an expert meeting analyst. "
            "Below are decision findings extracted from multiple transcript chunks. "
            "Merge all findings into ONE final list. "
            "Remove duplicates and ignore 'No key decisions found' or irrelevant entries. "
            "Do not invent decisions. "
            "If no decisions exist, say 'No key decisions found.' "
            "Format as a numbered list."
        )
    
    return run_on_chunks(transcript, chain, final_prompt)


def extract_questions(transcript: str) -> str:
    chain = build_chain(
        "From the meeting transcript, extract all unresolved questions "
        "or topics needing follow-up. Format as a numbered list. "
        "If none found say 'No open questions found.'"
    )
    final_prompt = (
        "You are an expert meeting analyst. "
        "Below are questions extracted from multiple transcript chunks. "
        "Merge all questions into ONE final list. "
        "Remove duplicate questions and ignore 'NONE'. "
        "Do not invent questions that are not present in the findings. "
        "If no unresolved questions exist, say 'No open questions found.' "
        "Format the final answer as a numbered list."
    )
    

    return run_on_chunks(transcript, chain, final_prompt)