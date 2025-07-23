# Security and Privacy Utilities
import os
import re
import logging
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecurityManager:
    """Handles security validations and privacy protection"""
    
    def __init__(self):
        self.failed_attempts = {}  # Rate limiting storage
        self.max_attempts = 5
        self.timeout_duration = 300  # 5 minutes
    
    def validate_environment_variables(self) -> Dict[str, bool]:
        """Validate all required environment variables are present and secure"""
        required_vars = {
            'BOT_TOKEN': self._validate_bot_token,
            'GEMINI_API_KEY': self._validate_gemini_key,
            'ADMIN_USER_ID': self._validate_user_id
        }
        
        optional_vars = {
            'NEWS_API_KEY': self._validate_news_key
        }
        
        results = {}
        critical_missing = []
        
        # Check required variables
        for var_name, validator in required_vars.items():
            value = os.getenv(var_name)
            if not value:
                results[var_name] = False
                critical_missing.append(var_name)
                logger.error(f"❌ Required environment variable {var_name} is missing")
            else:
                is_valid = validator(value)
                results[var_name] = is_valid
                if is_valid:
                    logger.info(f"✅ {var_name} is properly configured")
                else:
                    logger.error(f"❌ {var_name} format is invalid")
        
        # Check optional variables
        for var_name, validator in optional_vars.items():
            value = os.getenv(var_name)
            if value:
                is_valid = validator(value)
                results[var_name] = is_valid
                if is_valid:
                    logger.info(f"✅ {var_name} (optional) is properly configured")
                else:
                    logger.warning(f"⚠️ {var_name} format is invalid")
            else:
                logger.info(f"ℹ️ {var_name} (optional) not configured")
        
        if critical_missing:
            raise ValueError(f"Critical environment variables missing: {', '.join(critical_missing)}")
        
        return results
    
    def _validate_bot_token(self, token: str) -> bool:
        """Validate Telegram bot token format"""
        # Telegram bot tokens follow pattern: <bot_id>:<token>
        pattern = r'^\d{8,10}:[A-Za-z0-9_-]{35}$'
        return bool(re.match(pattern, token))
    
    def _validate_gemini_key(self, key: str) -> bool:
        """Validate Google Gemini API key format"""
        # Google API keys typically start with AIza and are 39 characters
        pattern = r'^AIza[A-Za-z0-9_-]{35}$'
        return bool(re.match(pattern, key))
    
    def _validate_news_key(self, key: str) -> bool:
        """Validate News API key format"""
        # News API keys are typically 32 character hex strings
        pattern = r'^[a-f0-9]{32}$'
        return bool(re.match(pattern, key))
    
    def _validate_user_id(self, user_id: str) -> bool:
        """Validate Telegram user ID format"""
        # Telegram user IDs are numeric, typically 9-10 digits
        try:
            uid = int(user_id)
            return 100000000 <= uid <= 9999999999  # Reasonable range
        except ValueError:
            return False
    
    def sanitize_user_input(self, text: str, max_length: int = 4000) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters and limit length
        sanitized = text[:max_length]
        
        # Remove SQL injection patterns
        dangerous_patterns = [
            r'--',  # SQL comments
            r'/\*.*?\*/',  # Multi-line comments
            r';\s*(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER)',  # SQL commands
            r'<script.*?</script>',  # Script tags
            r'javascript:',  # JavaScript protocol
            r'vbscript:',  # VBScript protocol
        ]
        
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    def check_rate_limit(self, user_id: int, action: str = "default") -> bool:
        """Check if user is rate limited for specific action"""
        key = f"{user_id}_{action}"
        current_time = datetime.now()
        
        if key in self.failed_attempts:
            attempts, last_attempt = self.failed_attempts[key]
            
            # Reset if timeout period has passed
            if current_time - last_attempt > timedelta(seconds=self.timeout_duration):
                del self.failed_attempts[key]
                return True
            
            # Check if user exceeded attempts
            if attempts >= self.max_attempts:
                logger.warning(f"User {user_id} rate limited for action {action}")
                return False
        
        return True
    
    def record_failed_attempt(self, user_id: int, action: str = "default"):
        """Record a failed attempt for rate limiting"""
        key = f"{user_id}_{action}"
        current_time = datetime.now()
        
        if key in self.failed_attempts:
            attempts, _ = self.failed_attempts[key]
            self.failed_attempts[key] = (attempts + 1, current_time)
        else:
            self.failed_attempts[key] = (1, current_time)
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for logging purposes"""
        return hashlib.sha256(data.encode()).hexdigest()[:8]
    
    def mask_api_key(self, api_key: str) -> str:
        """Mask API key for safe logging"""
        if len(api_key) <= 8:
            return "*" * len(api_key)
        return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
    
    def validate_file_permissions(self) -> List[str]:
        """Check file permissions for security"""
        issues = []
        
        # Check database directory permissions
        db_path = "database"
        if os.path.exists(db_path):
            try:
                stat_info = os.stat(db_path)
                # Check if directory is world-readable (not secure)
                if stat_info.st_mode & 0o044:
                    issues.append(f"Database directory {db_path} has world-readable permissions")
            except Exception as e:
                logger.warning(f"Could not check permissions for {db_path}: {e}")
        
        # Check for sensitive files in wrong locations
        sensitive_files = ['.env', 'api_keys.txt', 'secrets.txt', 'config.ini']
        for file in sensitive_files:
            if os.path.exists(file):
                issues.append(f"Sensitive file {file} found in project root")
        
        return issues

class PrivacyManager:
    """Handles user privacy and data protection"""
    
    def __init__(self):
        self.data_retention_days = 90
        self.log_retention_days = 28
    
    def anonymize_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize user data for analytics"""
        anonymized = {}
        
        # Keep only non-identifying information
        safe_fields = [
            'learning_streak', 'quiz_scores', 'vocab_learned',
            'grammar_attempts', 'content_preferences'
        ]
        
        for field in safe_fields:
            if field in user_data:
                anonymized[field] = user_data[field]
        
        # Add anonymized identifier
        if 'user_id' in user_data:
            anonymized['anon_id'] = hashlib.sha256(
                str(user_data['user_id']).encode()
            ).hexdigest()[:12]
        
        return anonymized
    
    def should_purge_user_data(self, last_activity: datetime) -> bool:
        """Check if user data should be purged due to inactivity"""
        cutoff_date = datetime.now() - timedelta(days=self.data_retention_days)
        return last_activity < cutoff_date
    
    def get_user_data_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summary of data stored for a user (for privacy requests)"""
        # This would query the actual database
        return {
            'data_types': [
                'Telegram ID and username',
                'Learning progress and statistics',
                'Quiz results and performance',
                'Grammar feedback history',
                'Content preferences'
            ],
            'retention_period': f"{self.data_retention_days} days",
            'data_sharing': 'No data shared with third parties',
            'deletion_policy': 'Data automatically purged after inactivity period'
        }
