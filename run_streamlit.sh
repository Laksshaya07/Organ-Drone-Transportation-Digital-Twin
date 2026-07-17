#!/bin/bash
# Ignore any passed arguments (such as --port and --host from the npm run dev execution)
streamlit run app.py --server.port 3000 --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false
