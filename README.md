# Hyper-Personalized AI Tax Optimizer

## Overview
A production-grade Tax Optimization and Capital Allocation Engine specifically designed for the Indian Income Tax ecosystem. This system models intricate tax regimes, automatically locates unutilized deductions, and recommends strict mathematical allocations across investment instruments to minimize total tax liability.

The platform functions as an automated quantitative Personal Chartered Accountant, bypassing static rule-based calculators in favor of dynamic Linear Programming (via PuLP) to solve multi-variable tax constraints.

## Architecture & Technology Stack

The application is structured as a decoupled web application with the following core technologies:

### Backend Engine (FastAPI)
*   **Python 3.x**: Core computational runtime.
*   **FastAPI**: High-performance REST API framework serving the tax optimization models.
*   **PuLP**: Linear programming library utilized to solve for absolute maximum tax savings against user risk profiles and liquidity constraints (e.g., balancing ELSS equity exposure vs. PPF duration).
*   **pdfplumber & Google GenAI (Gemini)**: A robust 3-pass extraction pipeline for natively parsing structural data from standard PDF Form 16s and Salary Slips.

### Frontend Client (Next.js)
*   **Next.js 14 & React**: Server-side rendering and client routing for the onboarding wizard.
*   **Tailwind CSS**: Strict, minimalist design system tailored for a premium fintech aesthetic. 
*   **Framer Motion**: Smooth, native-feeling component transitions.
*   **Recharts**: Data visualization for the Tax Elimination Speedometer and Capital Deployment Bar Charts.

## Key Features

*   **Deterministic Tax Modeling**: Native handling of FY-keyed slabs, explicit Section 87A marginal relief computations, and conditional surcharge/cess additions without reliance on third-party calculators.
*   **Automated Data Extraction**: Secure local and localized cloud NLP tools for extracting raw financial variables directly from tax documents.
*   **HRA Topology Optimization**: Dynamically assesses the 'Rule of 3' limits (Actual HRA received, 40/50% of Basic, Rent - 10% of Basic) to calculate the precise threshold where forfeiting HRA for the New Regime mathematically benefits the user.
*   **Corporate NPS Restructuring**: Assesses Gross Salary to automatically recommend Section 80CCD(2) employer contributions, restructuring the CTC natively for tax shields.

## Running the Application Locally

The application requires both the Python backend and the Node.js frontend to be running simultaneously.

### 1. Backend Server Initialization
Navigate to the root directory and install Python dependencies, then launch the Uvicorn server:

```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Client Initialization
Open a new terminal session, navigate to the `frontend` directory, install packages, and initialize the Next.js development server:

```bash
cd frontend
npm install
npm run dev
```

Navigate to `http://localhost:3000` (or the port specified by Next.js) in your browser to access the application.

## License
MIT License. See LICENSE file for details.
