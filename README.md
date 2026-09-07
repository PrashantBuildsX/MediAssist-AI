# MediAssist AI

### An Intelligent Clinical Decision Support Platform using RAG and Large Language Models

## Overview

MediAssist AI is an AI-powered clinical decision support platform designed
to help doctors retrieve, summarize, compare, and analyze patient medical
records using Retrieval-Augmented Generation (RAG) and Large Language Models
(LLMs).

The platform provides separate portals for patients and doctors.

## Objectives

- Manage patient medical records digitally.
- Allow patients to upload and manage their medical documents.
- Allow doctors to securely access authorized patient records.
- Retrieve relevant information from patient medical history.
- Generate AI-assisted summaries and responses.
- Compare medical reports and identify relevant changes over time.
- Provide grounded responses using RAG rather than relying only on the LLM's
  internal knowledge.

## Main Modules

### Patient Portal
- Registration and login
- Profile management
- Medical record upload
- Medical history

### Doctor Portal
- Doctor login
- Patient search
- Patient medical history
- AI-assisted medical record analysis
- Medical record summarization
- Report comparison
- Patient timeline
- Consultation notes

## Technology Stack

- Frontend: React, Tailwind CSS
- Backend: Python, FastAPI
- Database: PostgreSQL
- RAG: LangChain, Chroma
- Embeddings: Sentence Transformers
- LLM: Llama via Groq API
- Document Processing: PyMuPDF / OCR
- Development: Git, GitHub, Docker, Postman

## System Architecture

The detailed system architecture will be documented in:

`docs/architecture/`

## Project Status

🚧 Development Phase — In Progress

## Team

Major Project — 4th Year