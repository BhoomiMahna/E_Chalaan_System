"""
Query Agent — Converts natural language questions using Local LLM and Vector DB.
Maintains fallback keyword parser for structured database results to preserve UI compatibility.
"""
import logging
from datetime import datetime
from services.rag_service import RAGService

logger = logging.getLogger(__name__)

class QueryAgent:
    """Answers natural language queries using RAG and returns tabular fallback data."""

    def __init__(self):
        self.rag_service = RAGService()

    def process(self, query_text):
        """Process a natural language query and return results."""
        try:
            # Query the Local RAG pipeline for an intelligent text answer
            rag_answer = self.rag_service.ask(query_text)

            # Get structured data from fallback to maintain UI table compatibility
            fallback_result = self._process_with_fallback(query_text)
            
            # Combine the results. The frontend ignores extra fields, so adding 'answer' is safe.
            return {
                'query': query_text,
                'sql': fallback_result.get('sql', ''),
                'results': fallback_result.get('results', []),
                'count': fallback_result.get('count', 0),
                'answer': rag_answer  # New field powered by local LLM
            }
        except Exception as e:
            logger.error(f"NLQ processing failed: {e}")
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
        """Keyword-based fallback to return tabular results."""
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
