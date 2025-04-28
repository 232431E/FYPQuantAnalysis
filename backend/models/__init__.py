# backend/models/__init__.py
from .user_model import User
from .alert_model import Alert
from .feedback_model import Feedback
from .prompt_model import PromptVersion, prompt_model_init  # Import the init function
from .report_model import Report, report_model_init
from .data_model import Company, FinancialData, News, data_model_init

__all__ = ['Company', 'FinancialData', 'Report', 'News', 'User', 'Alert', 'Feedback', 'Prompt', 'data_model_init',
           'report_model_init', 'prompt_model_init']  # Include prompt_model_init in __all__
# Import the models here as well. This can sometimes help SQLAlchemy
# to see them during the initialization phase.
Company  # noqa: F401  # Suppress "imported but unused"
FinancialData  # noqa: F401
Report  # noqa: F401
News  # noqa: F401
User  # noqa: F401
Alert  # noqa: F401
Feedback  # noqa: F401
PromptVersion  # noqa: F401