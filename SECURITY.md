# 🔒 Security & Privacy Policy

## 🛡️ Security Measures

### Environment Variables Protection
- All sensitive data (API keys, tokens) must be stored in environment variables
- Never commit `.env` files or files containing secrets to version control
- Use `.env.production` as a template only with placeholder values
- Validate all environment variables at startup

### API Key Security
- **Telegram Bot Token**: Keep secure, rotates if compromised
- **Gemini API Key**: Restrict by IP and domain when possible
- **News API Key**: Use rate limiting and monitoring
- **Admin User ID**: Never expose in logs or error messages

### Database Security
- Use SQLite with proper file permissions (600)
- Sanitize all user inputs to prevent SQL injection
- Regular database backups (exclude from git)
- Implement user data retention policies

### Code Security
- Input validation on all user messages and commands
- Rate limiting on API calls and user interactions
- Error handling that doesn't expose internal details
- Logging that excludes sensitive information

## 🔐 Privacy Protection

### User Data Handling
- Collect only necessary user information:
  - Telegram ID (for bot functionality)
  - Username (optional, for display)
  - Learning progress (for personalization)
  - Quiz results (for improvement)

### Data Storage
- Local SQLite database (not shared with third parties)
- User data encrypted at rest when possible
- No personal messages stored permanently
- Grammar analysis data anonymized

### Data Retention
- User progress data: Retained while user is active
- Inactive users: Data purged after 90 days
- Logs: Rotated every 7 days, max 4 weeks retention
- Quiz results: Aggregated anonymously for improvements

### Third-Party APIs
- **Google Gemini**: Content generation only, no user data shared
- **News API**: Public data only, no user identification
- **Telegram**: Standard bot API, user privacy respected

## 🚨 Incident Response

### If API Keys Are Compromised:
1. Immediately revoke the compromised keys
2. Generate new keys from respective services
3. Update environment variables in production
4. Monitor for unauthorized usage
5. Review access logs

### Data Breach Protocol:
1. Immediate assessment of affected data
2. Secure the breach point
3. User notification if personal data affected
4. Implement additional security measures
5. Document incident and lessons learned

## ✅ Security Checklist

### Before Deployment:
- [ ] All API keys removed from tracked files
- [ ] Environment variables properly configured
- [ ] Database file permissions set correctly
- [ ] Error messages sanitized
- [ ] Rate limiting implemented
- [ ] Input validation in place
- [ ] Logging configured properly

### Regular Security Maintenance:
- [ ] API key rotation (quarterly)
- [ ] Dependency updates (monthly)
- [ ] Security log review (weekly)
- [ ] User data cleanup (monthly)
- [ ] Backup verification (weekly)

## 📞 Security Contact

For security issues or questions:
- Create a private GitHub issue with label `security`
- Email: [Your secure contact email]
- Response time: 24-48 hours for critical issues

## 🔄 Policy Updates

This security policy is reviewed and updated:
- When new features are added
- After security incidents
- At least every 6 months
- When regulations change

Last updated: July 23, 2025
