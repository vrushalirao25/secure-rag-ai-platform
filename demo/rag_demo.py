"""
Secure RAG AI Platform - Demo

This script demonstrates a simplified RAG (Retrieval-Augmented Generation) flow:

Query → Embedding → Retrieval → Context → Generation

Purpose:
- Validate RAG architecture
- Demonstrate retrieval + generation
- Showcase platform-level thinking (not production implementation)

Production Architecture (conceptual):
- Data Layer: Amazon S3
- Retrieval: Amazon OpenSearch (vector search)
- Model: Amazon Bedrock
- Orchestration: AWS Lambda

Note:
This demo uses in-memory retrieval to avoid infrastructure setup.
"""

import boto3
import json
import math

# ── Configuration ───────────────────────────────────────────────
MODEL_ID = "amazon.titan-text-express-v1"
EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v1"
TOP_K = 2

# ── Sample Knowledge Base (simulates S3 + OpenSearch) ───────────
DOCUMENTS = [
    "Model retraining pipelines are orchestrated using Apache Airflow with automated validation and deployment approval gates.", 
    "Production deployment requires monitoring validation including API health checks, prediction logging, CloudWatch alerts, and database write verification.",
    "The platform uses Amazon S3 for artifact storage and Amazon Bedrock for GenAI-powered summarization workflows.",
    "Platform KPIs include prediction accuracy, SLA breach reduction, inference latency, and deployment stability.", 
    "Role-based IAM policies restrict access between data ingestion, model inference, and deployment workflows.",
    "Fallback strategies are implemented to handle model service degradation and retrieval failures.", 
    "Observability pipelines capture inference metrics, failure signals, and operational logs for monitoring and governance."
]

# ── Bedrock Client ──────────────────────────────────────────────
def get_bedrock_client():
    return boto3.client("bedrock-runtime", region_name="us-east-1")


# ── Platform Health Check ──────────────────────────────────────
def health_check(client):
    signals = {
        "knowledge_base_loaded": len(DOCUMENTS) > 0,
        "bedrock_client_ready": client is not None,
        "embedding_model_set": EMBEDDING_MODEL_ID != "",
        "generation_model_set": MODEL_ID != "",
        "top_k_configured": TOP_K > 0
    }

    status = "HEALTHY" if all(signals.values()) else "DEGRADED"

    print(f"\nPlatform Health: {status}")
    for signal, value in signals.items():
        print(f"  {'✓' if value else '✗'} {signal}")

    return status


# ── Embedding Function ─────────────────────────────────────────
def get_embedding(text, client):
    try:
        response = client.invoke_model(
            modelId=EMBEDDING_MODEL_ID,
            body=json.dumps({"inputText": text})
        )
        return json.loads(response["body"].read())["embedding"]
    except Exception:
        # Fallback: simple mock embedding
        return [float(ord(c) % 10) for c in text[:50]]


# ── Cosine Similarity ──────────────────────────────────────────
def cosine_similarity(a, b):
    length = min(len(a), len(b))
    a, b = a[:length], b[:length]

    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))

    if mag_a == 0 or mag_b == 0:
        return 0

    return dot / (mag_a * mag_b)


# ── Retrieval Step (Core of RAG) ───────────────────────────────
def retrieve_documents(query, client):
    query_embedding = get_embedding(query, client)

    scored = []
    for doc in DOCUMENTS:
        doc_embedding = get_embedding(doc, client)
        score = cosine_similarity(query_embedding, doc_embedding)
        scored.append((doc, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in scored[:TOP_K]]


# ── Generation Step ────────────────────────────────────────────
def generate_response(query, context_docs, client):
    context = "\n".join(context_docs)

    prompt = f"""
Answer the question using ONLY the context below.

Context:
{context}

Question:
{query}

Answer:
"""

    try:
        response = client.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 300,
                    "temperature": 0.3
                }
            })
        )

        result = json.loads(response["body"].read())
        return result["results"][0]["outputText"]

    except Exception:
        # Fallback strategy:
        # If Bedrock is unavailable, return retrieved context
        return f"[Fallback response]\n\nContext:\n{context}"


# ── Main Flow ─────────────────────────────────────────────────
def run_demo():
    client = get_bedrock_client()

    # Platform health validation
    health_check(client)

    query = "How are model retraining and deployment managed?"

    print("\n--- RAG DEMO ---")
    print("Query:", query)

    # Step 1: Retrieve
    docs = retrieve_documents(query, client)
    print("\nRetrieved Documents:")
    for d in docs:
        print("-", d)

    # Step 2: Generate
    answer = generate_response(query, docs, client)

    print("\nGenerated Answer:")
    print(answer)


if __name__ == "__main__":
    run_demo()
