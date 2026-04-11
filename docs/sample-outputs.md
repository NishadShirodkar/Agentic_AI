# Sample Outputs

These are representative outputs from the current system shape. They are shortened for readability, but they match the structure the app returns.

## 1. Happy Path

**Query**

Compare the top 3 open-source vector databases for RAG systems.

**Result**

```json
{
  "question": "Compare the top 3 open-source vector databases for RAG systems.",
  "short_answer": "Qdrant is strong for performance and filtering, Weaviate is strong for hybrid search and schema support, and Milvus is strong for large-scale vector workloads.",
  "key_findings": [
    "Qdrant is a good fit when payload filtering and fast retrieval matter.",
    "Weaviate offers a flexible schema and strong hybrid search capabilities.",
    "Milvus is well suited for high-scale vector search workloads."
  ],
  "sources": [
    "https://qdrant.tech/",
    "https://weaviate.io/",
    "https://milvus.io/"
  ],
  "confidence": "High",
  "limitations": [
    "Comparison depends on the quality of available web sources."
  ],
  "next_steps": [
    "Benchmark each database on your own dataset.",
    "Check deployment complexity and hosting requirements."
  ]
}
```

## 2. Failure / Edge Case

**Query**

Find detailed information about a very new startup called "NovaQuery" that has no public website, documentation, or press coverage.

**Result**

```json
{
  "question": "Find detailed information about a very new startup called \"NovaQuery\" that has no public website, documentation, or press coverage.",
  "short_answer": "Insufficient data to answer the question.",
  "key_findings": [],
  "sources": [],
  "confidence": "Low",
  "limitations": [
    "No reliable sources found"
  ],
  "next_steps": [
    "Try refining the query",
    "Provide a company domain, founder name, or location"
  ]
}
```

## 3. Partial / Noisy Input

**Query**

Compare the top 3 open-source vector databases for RAG systems, but only use sources published in the last 24 hours.

**Result**

```json
{
  "question": "Compare the top 3 open-source vector databases for RAG systems, but only use sources published in the last 24 hours.",
  "short_answer": "The query is too restrictive, so the system returns a smaller evidence set and a lower-confidence summary.",
  "key_findings": [
    "Recent-source filtering reduces the number of usable pages.",
    "The final answer depends on what fresh content is available at runtime."
  ],
  "sources": [
    "https://qdrant.tech/",
    "https://weaviate.io/"
  ],
  "confidence": "Medium",
  "limitations": [
    "Recent-only constraints can reduce source coverage."
  ],
  "next_steps": [
    "Relax the recency constraint",
    "Re-run with a broader query"
  ]
}
```
