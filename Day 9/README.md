# 🎯 Intent-Based Job Role Recommender

> A LangChain-powered Streamlit app that analyzes a student's profile (SOP, GitHub summary, resume) to recommend job roles aligned with their intent, skills, and motivation using Retrieval-Augmented Generation and multi-agent reasoning.

## 🚀 Features

- Multi-Agent System  
- Retrieval-Augmented Generation (RAG)  
- Google Gemini LLM + Embeddings  
- PDF/DOCX support  
- Domain + Experience filters  
- PDF Report Export  

## 🧠 Agents Overview

This app uses **5 AI agents** implemented with `langchain.agents.Tool` and orchestrated via an `AgentExecutor`.

| Agent Name            | Role Description                                                           |
|-----------------------|------------------------------------------------------------------------------|
| 1. Intent Extractor   | Extracts user's interests, motivation, and core skills                      |
| 2. Pattern Analyzer   | Detects alignment with career success patterns and identifies gaps          |
| 3. Role Matcher       | Suggests personalized job roles with reasons and scores                     |
| 4. Misalignment Flagger | Identifies inconsistencies between goals and roles                        |
| 5. Resume Tailor      | Suggests resume improvements based on target roles                          |

## 🧱 Architecture

Uploaded File ➝ Text Extractor ➝ Text Splitter ➝ ChromaDB + Gemini ➝ Agent Executor ➝ Output

## 🛠️ Tech Stack

- LangChain (agents, retrievers, prompts, chains)  
- Streamlit – UI Framework  
- Gemini 1.5 Flash – LLM  
- Google GenAI Embeddings  
- ChromaDB – Vector Store  
- PyMuPDF – PDF Parsing  

## 📁 File Upload

Upload a `.pdf` or `.docx` file (SOP, resume, or GitHub summary), choose a target job domain and experience level, and click **Analyze**.

## 📄 Output

You’ll get:
- Intent Summary  
- Pattern Analysis  
- Recommended Roles  
- Misalignment Warnings  
- Resume Suggestions  

## ✅ Evaluation Criteria Mapping

| Criteria                  | Status                          |
|---------------------------|----------------------------------|
| Agent Implementation      | ✅ 5 Tools used as Agents         |
| RAG Implementation        | ✅ Chroma + Retriever + Gemini    |
| GenAI Usage               | ✅ Gemini 1.5 Flash               |
| Solution Impact           | ✅ Personalized suggestions       |
| Remarks / Design          | ✅ Modular + agent-based          |
| Docs / GitHub Structure   | ✅ (This README!)                 |

---

## 🙌 Author

Built by **Varadharajan** as part of an AI workshop submission.
