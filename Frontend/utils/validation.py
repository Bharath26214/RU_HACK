"""
Validation module for form validation logic.
Handles validation of required fields, max counts, and data integrity.
"""

import streamlit as st
from typing import List, Dict, Any, Tuple


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class FormValidator:
    """Handles form validation for the Streamlit app."""
    
    # Constants for validation limits
    MAX_LOCATIONS = 6
    MAX_POSITIONS = 5
    MAX_PREFERENCES = 10
    
    # Required fields
    REQUIRED_FIELDS = {
        'resume_text': 'Resume text',
        'preferred_locations': 'Preferred locations',
        'selected_preferences': 'Job preferences'
    }
    
    @staticmethod
    def validate_required_fields(session_state: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that all required fields are filled.
        
        Args:
            session_state: Streamlit session state dictionary
            
        Returns:
            Tuple of (is_valid, list_of_missing_fields)
        """
        missing_fields = []
        
        # Check resume text
        if not session_state.get('raw_resume_text', '').strip():
            missing_fields.append('Resume text')
        
        # Check preferred locations
        if not session_state.get('preferred_locations', []):
            missing_fields.append('Preferred locations')
        
        # Check job preferences
        if not session_state.get('selected_preferences', []):
            missing_fields.append('Job preferences')
        
        return len(missing_fields) == 0, missing_fields
    
    @staticmethod
    def validate_max_counts(session_state: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that count limits are not exceeded.
        
        Args:
            session_state: Streamlit session state dictionary
            
        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []
        
        # Check locations count
        locations = session_state.get('preferred_locations', [])
        if len(locations) > FormValidator.MAX_LOCATIONS:
            violations.append(f'Preferred locations ({len(locations)}) exceeds maximum of {FormValidator.MAX_LOCATIONS}')
        
        # Check positions count
        positions = session_state.get('selected_positions', [])
        if len(positions) > FormValidator.MAX_POSITIONS:
            violations.append(f'Target positions ({len(positions)}) exceeds maximum of {FormValidator.MAX_POSITIONS}')
        
        # Check preferences count
        preferences = session_state.get('selected_preferences', [])
        if len(preferences) > FormValidator.MAX_PREFERENCES:
            violations.append(f'Job preferences ({len(preferences)}) exceeds maximum of {FormValidator.MAX_PREFERENCES}')
        
        return len(violations) == 0, violations
    
    @staticmethod
    def validate_file_upload(uploaded_file) -> Tuple[bool, str]:
        """
        Validate uploaded file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if uploaded_file is None:
            return True, ""  # No file uploaded is valid
        
        # Check file size (limit to 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            return False, f"File size ({uploaded_file.size / 1024 / 1024:.1f}MB) exceeds maximum allowed size (10MB)"
        
        # Check file type
        allowed_types = ['pdf', 'docx', 'txt']
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in allowed_types:
            return False, f"File type '{file_extension}' is not supported. Allowed types: {', '.join(allowed_types)}"
        
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format.
        
        Args:
            email: Email string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return True, ""  # Empty email is valid (optional field)
        
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format.
        
        Args:
            phone: Phone string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not phone:
            return True, ""  # Empty phone is valid (optional field)
        
        import re
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        # Check if it has 10-15 digits (international format)
        if len(digits_only) < 10 or len(digits_only) > 15:
            return False, "Phone number must be 10-15 digits"
        
        return True, ""
    
    @staticmethod
    def validate_all(session_state: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Perform all validations.
        
        Args:
            session_state: Streamlit session state dictionary
            
        Returns:
            Tuple of (is_valid, list_of_all_errors)
        """
        all_errors = []
        
        # Validate required fields
        is_valid_required, missing_fields = FormValidator.validate_required_fields(session_state)
        if not is_valid_required:
            all_errors.extend([f"Missing required field: {field}" for field in missing_fields])
        
        # Validate max counts
        is_valid_counts, count_violations = FormValidator.validate_max_counts(session_state)
        if not is_valid_counts:
            all_errors.extend(count_violations)
        
        # Validate email if provided
        email = session_state.get('email', '')
        is_valid_email, email_error = FormValidator.validate_email(email)
        if not is_valid_email:
            all_errors.append(f"Email validation error: {email_error}")
        
        # Validate phone if provided
        phone = session_state.get('contact', '')
        is_valid_phone, phone_error = FormValidator.validate_phone(phone)
        if not is_valid_phone:
            all_errors.append(f"Phone validation error: {phone_error}")
        
        return len(all_errors) == 0, all_errors
    
    @staticmethod
    def enforce_max_counts(session_state: Dict[str, Any]) -> None:
        """
        Enforce maximum counts by trimming lists to limits.
        This is called silently without showing errors to the user.
        
        Args:
            session_state: Streamlit session state dictionary (modified in place)
        """
        # Trim locations
        locations = session_state.get('preferred_locations', [])
        if len(locations) > FormValidator.MAX_LOCATIONS:
            session_state['preferred_locations'] = locations[:FormValidator.MAX_LOCATIONS]
        
        # Trim positions
        positions = session_state.get('selected_positions', [])
        if len(positions) > FormValidator.MAX_POSITIONS:
            session_state['selected_positions'] = positions[:FormValidator.MAX_POSITIONS]
        
        # Trim preferences
        preferences = session_state.get('selected_preferences', [])
        if len(preferences) > FormValidator.MAX_PREFERENCES:
            session_state['selected_preferences'] = preferences[:FormValidator.MAX_PREFERENCES]


def validate_form_before_analysis(session_state: Dict[str, Any]) -> bool:
    """
    Validate form before running analysis. Returns True if valid, False otherwise.
    This function performs silent validation without showing errors to the user.
    
    Args:
        session_state: Streamlit session state dictionary
        
    Returns:
        bool: True if form is valid, False otherwise
    """
    # Enforce max counts silently
    FormValidator.enforce_max_counts(session_state)
    
    # Check if all required fields are filled
    is_valid, missing_fields = FormValidator.validate_required_fields(session_state)
    
    if not is_valid:
        # Don't show error to user, just return False
        return False
    
    return True
