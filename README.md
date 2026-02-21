# ⚡ Synapse Data Intelligence
**HackFest 2.0 Submission | Track: Intelligent Data Dictionary Agent**

Synapse is an enterprise-grade AI Data Dictionary Agent. It connects to relational databases, extracts schema metadata, performs live data quality analysis, and uses the Gemini 2.5 LLM to provide natural language business context.

## 🚀 Tech Stack
* **Frontend/UI:** Streamlit (Custom Glassmorphism CSS)
* **Backend:** Python, SQLite, Pandas
* **AI Engine:** Google Cloud Gemini API
* **Dataset:** Olist Brazilian E-Commerce (100k+ rows)

## 🛠️ How to Run Locally
1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Gemini API Key inside `app.py`.
4. Download the [Olist Dataset from Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and place the CSV files in the root folder.
5. Run the app: `python -m streamlit run app.py`