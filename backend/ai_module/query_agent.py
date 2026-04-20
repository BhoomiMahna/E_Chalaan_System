"""
Query Agent — Converts natural language questions to SQL queries.
Uses Google Gemini API for NL→SQL conversion with a fallback keyword parser.
"""
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class QueryAgent:
    """Converts natural language queries to SQL and executes them."""

    def __init__(self):
        self.gemini_model = None
        self._init_llm()

    def _init_llm(self):
        """Initialize Google Gemini client."""
        try:
            from config import Config
            api_key = Config.GEMINI_API_KEY
            if not api_key:
                logger.info("No GEMINI_API_KEY set. Using keyword-based fallback.")
                return
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("Gemini API initialized for query agent")
        except ImportError:
            logger.warning("google-generativeai not installed. Using fallback.")
        except Exception as e:
            logger.warning(f"Gemini init failed: {e}. Using fallback.")

    def process(self, query_text):
        """Process a natural language query and return results."""
        if self.gemini_model:
            return self._process_with_llm(query_text)
        return self._process_with_fallback(query_text)

    def _process_with_llm(self, query_text):
        """Use Gemini to convert NL to SQL and execute."""
        schema = """
        Table: violations
        Columns:
        - id (INTEGER, primary key)
        - vehicle_number (VARCHAR(20))
        - owner_name (VARCHAR(100))
        - address (VARCHAR(200))
        - violation_type (VARCHAR(20)) -- values: 'no_helmet', 'red_light'
        - fine_amount (INTEGER) -- 1000 for no_helmet, 5000 for red_light
        - date_time (DATETIME)
        - location (VARCHAR(100))
        - status (VARCHAR(20)) -- values: 'pending', 'paid', 'disputed'
        - image_path (VARCHAR(200))
        - confidence (FLOAT)
        """

        prompt = f"""Convert this natural language query to a SQLite SELECT query.
Database schema: {schema}
Today's date: {datetime.now().strftime('%Y-%m-%d')}
Query: "{query_text}"

Rules:
- Return ONLY the SQL query, no explanation
- Use SQLite date functions (date(), strftime())
- For "today", use date(date_time) = date('now')
- For "this week", use date_time >= date('now', '-7 days')
- For "this month", use date_time >= date('now', '-30 days')
- Always use SELECT, never UPDATE/DELETE/INSERT
- Limit results to 50 rows max
- If asking for a count/total, use COUNT(*) or SUM()
"""
        try:
            response = self.gemini_model.generate_content(prompt)
            sql = response.text.strip()
            # Clean markdown code blocks if present
            sql = re.sub(r'```sql\s*', '', sql)
            sql = re.sub(r'```\s*', '', sql)
            sql = sql.strip()

            # Safety: only allow SELECT
            if not sql.upper().startswith('SELECT'):
                return {'query': sql, 'error': 'Only SELECT queries allowed', 'results': []}

            return self._execute_sql(sql, query_text)
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            return self._process_with_fallback(query_text)

    def _execute_sql(self, sql, original_query=''):
        """Execute SQL safely and return results."""
        from models.violation import db
        try:
            result = db.session.execute(db.text(sql))
            rows = result.fetchall()
            columns = list(result.keys()) if result.keys() else []
            data = [dict(zip(columns, row)) for row in rows]
            # Convert datetime objects to strings
            for row in data:
                for k, v in row.items():
                    if isinstance(v, datetime):
                        row[k] = v.isoformat()
            return {
                'query': original_query,
                'sql': sql,
                'results': data,
                'count': len(data)
            }
        except Exception as e:
            return {'query': original_query, 'sql': sql, 'error': str(e), 'results': []}

    def _process_with_fallback(self, query_text):
        """Keyword-based fallback when LLM is unavailable."""
        q = query_text.lower()
        sql = None

        if 'today' in q and ('helmet' in q or 'no_helmet' in q):
            sql = "SELECT * FROM violations WHERE violation_type='no_helmet' AND date(date_time)=date('now') LIMIT 50"
        elif 'today' in q:
            sql = "SELECT * FROM violations WHERE date(date_time)=date('now') LIMIT 50"
        elif 'total fine' in q and 'week' in q:
            sql = "SELECT SUM(fine_amount) as total_fines, COUNT(*) as count FROM violations WHERE date_time >= date('now','-7 days')"
        elif 'total fine' in q:
            sql = "SELECT SUM(fine_amount) as total_fines FROM violations"
        elif 'most violation' in q and 'area' in q:
            sql = "SELECT location, COUNT(*) as count FROM violations GROUP BY location ORDER BY count DESC LIMIT 10"
        elif 'helmet' in q:
            sql = "SELECT * FROM violations WHERE violation_type='no_helmet' ORDER BY date_time DESC LIMIT 50"
        elif 'red light' in q or 'red_light' in q:
            sql = "SELECT * FROM violations WHERE violation_type='red_light' ORDER BY date_time DESC LIMIT 50"
        elif 'pending' in q:
            sql = "SELECT * FROM violations WHERE status='pending' ORDER BY date_time DESC LIMIT 50"
        elif 'count' in q or 'how many' in q:
            sql = "SELECT COUNT(*) as total FROM violations"
        else:
            sql = "SELECT * FROM violations ORDER BY date_time DESC LIMIT 20"

        return self._execute_sql(sql, query_text)
