"""
Explanation Agent — Generates human-readable violation explanations.
Uses template-based generation with optional LLM enhancement via Gemini.
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ExplanationAgent:
    """Generates natural language explanations for traffic violations."""

    VIOLATION_DESCRIPTIONS = {
        'no_helmet': 'the rider was detected without a helmet while riding a two-wheeler',
        'red_light': 'the vehicle was detected crossing the stop line while the traffic signal was red'
    }

    def __init__(self):
        self.gemini_model = None
        self._init_llm()

    def _init_llm(self):
        try:
            from config import Config
            api_key = Config.GEMINI_API_KEY
            if not api_key:
                return
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception:
            pass

    def explain(self, violation_dict):
        """
        Generate a detailed explanation for a violation.

        Args:
            violation_dict: Serialized violation record

        Returns:
            str: Human-readable explanation
        """
        # Generate base template explanation
        template_explanation = self._template_explain(violation_dict)

        # Enhance with LLM if available
        if self.gemini_model:
            try:
                return self._llm_enhance(violation_dict, template_explanation)
            except Exception as e:
                logger.warning(f"LLM enhancement failed: {e}")

        return template_explanation

    def _template_explain(self, v):
        """Generate explanation from template."""
        from models.violation_fine import ViolationFine
        
        vtype = v.get('violation_type', 'no_helmet')
        dt = v.get('date_time', '')
        if isinstance(dt, str) and dt:
            try:
                dt_obj = datetime.fromisoformat(dt)
                date_str = dt_obj.strftime('%d %B %Y')
                time_str = dt_obj.strftime('%H:%M')
            except Exception:
                date_str = dt
                time_str = ''
        else:
            date_str = str(dt)
            time_str = ''

        fine_record = ViolationFine.query.filter_by(violation_type=vtype).first()
        description = self.VIOLATION_DESCRIPTIONS.get(vtype, f"a {vtype.replace('_', ' ')} violation was detected")
        
        if fine_record:
            legal = f"As per traffic regulations, a {vtype.replace('_', ' ')} violation attracts a base fine of ₹{fine_record.base_amount:,}."
        else:
            legal = ""

        explanation = (
            f"📋 **Violation Report**\n\n"
            f"This vehicle (**{v.get('vehicle_number', 'N/A')}**), registered to "
            f"**{v.get('owner_name', 'Unknown')}**, was fined **₹{v.get('fine_amount', 0):,}** "
            f"on **{date_str}** at **{time_str}** because {description}.\n\n"
            f"📍 **Location**: {v.get('location', 'N/A')}\n"
            f"🔍 **Detection Confidence**: {v.get('confidence', 0):.1%}\n"
            f"📊 **Status**: {v.get('status', 'pending').title()}\n\n"
            f"⚖️ {legal}\n\n"
            f"The vehicle owner at address: {v.get('address', 'N/A')} "
            f"is advised to pay the fine within 30 days to avoid additional penalties."
        )
        return explanation

    def _llm_enhance(self, v, template):
        """Use Gemini to create a more detailed explanation."""
        prompt = f"""You are a traffic violation explanation system. Given this violation data and template,
generate a clear, professional, and empathetic explanation in 3-4 sentences.

Violation Data: Vehicle {v.get('vehicle_number')}, Type: {v.get('violation_type')},
Fine: ₹{v.get('fine_amount')}, Date: {v.get('date_time')}, Location: {v.get('location')},
Owner: {v.get('owner_name')}, Status: {v.get('status')}

Base template: {template}

Make it sound professional but human-friendly. Keep the markdown formatting. Include all factual details."""

        response = self.gemini_model.generate_content(prompt)
        return response.text.strip()
