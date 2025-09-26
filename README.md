# soc-streaming-detection
SOC-focused and detection-centric using Kafka

This project demonstrates how **Kafka, Spark Structured Streaming, and Delta Lake on MinIO** can be used to build a real-time pipeline for **cybersecurity threat detection**.  
The system ingests simulated authentication events, applies detection logic, and generates alerts for scenarios like brute-force logins and suspicious activity.

## Overview
- **Kafka** streams authentication/network events in real time  
- **Spark Structured Streaming** validates, enriches, and applies detection rules  
- **Delta Lake (Bronze, Silver, Gold)** stores data in structured layers  
- **Dead Letter Queue (DLQ)** handles invalid events  
- **Gold layer alerts** highlight potential security threats for SOC teams
