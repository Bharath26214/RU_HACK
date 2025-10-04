"""
Refactored Streamlit application using modular architecture.
This version uses separate modules for better maintainability.
"""

import streamlit as st
import time
import sys
import os

# Add the Frontend directory to Python path for imports
frontend_dir = os.path.dirname(os.path.abspath(__file__))
if frontend_dir not in sys.path:
    sys.path.insert(0, frontend_dir)

# Import our custom modules
from utils.validation import validate_form_before_analysis
from utils.resume_processor import handle_file_upload
from utils.data_models import STANDARD_LOCATIONS, STANDARD_POSITIONS, STANDARD_JOB_TYPES, ALL_STANDARD_PREFERENCES
from utils.backend_integration import send_resume_data_to_backend, analyze_resume_logic, generate_job_recommendations, print_ui_data_to_terminal
from utils.ui_components import (
    LoadingOverlay, CustomCSS, FormComponents, MultiselectWithCustom, 
    DisplayComponents, SessionStateManager
)
from utils.simple_multiselect import simple_multiselect_with_custom_input, simple_multiselect

# Set page config first
st.set_page_config(
    page_title="AI Career Optimization Tool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom styles
CustomCSS.apply_custom_styles()

# Constants
MAX_LOCATIONS = 6
MAX_POSITIONS = 5
MAX_JOB_TYPES = 4
MAX_PREFERENCES = 10


def show_resume_text_modal():
    """Show resume text editing in expander."""
    with st.expander("📝 Edit Resume Text", expanded=True):
        st.markdown("**Required:** This text will be analyzed by AI")
        
        # Resume text editor
        edited_text = st.text_area(
            "Final Resume Text Used for Analysis:",
            value=st.session_state.raw_resume_text,
            height=400,
            key='modal_resume_input',
            help="Edit your resume text here. This text will be used for AI analysis."
        )
        
        # Update session state
        st.session_state.raw_resume_text = edited_text
        
        # Action buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 Reset Text", key='reset_resume_btn'):
                st.session_state.raw_resume_text = ""
                st.rerun()
        
        with col2:
            if st.button("✅ Done Editing", key='done_resume_btn'):
                st.session_state.show_resume_modal = False
                st.rerun()
        
        st.info("💡 **Tip:** Manually edit the text above to ensure accuracy before running the analysis.")


def profile_analysis_tab():
    """Content for the Profile Analysis tab."""
    st.header("Profile Analysis & Data Extraction")
    st.markdown("---")

    # Info button explaining required fields
    FormComponents.info_button_with_tooltip()

    col_resume, col_prefs = st.columns(2)

    with col_resume:
        st.markdown("### Upload or Paste Resume *")

        uploaded_file = st.file_uploader(
            "Upload Resume (PDF, DOCX, or TXT)",
            type=['pdf', 'docx', 'txt'],
            help="For PDF/DOCX, please review the text area below as full conversion may require manual verification.",
            on_change=lambda: handle_file_upload(st.session_state.uploaded_file_key),
            key='uploaded_file_key'
        )

        # Resume text preview and edit button
        col1, col2 = st.columns([3, 1])
        with col1:
            # Show preview of resume text
            preview_text = st.session_state.raw_resume_text[:200] + "..." if len(st.session_state.raw_resume_text) > 200 else st.session_state.raw_resume_text
        st.text_area(
                "Resume Text Preview:",
                value=preview_text,
                height=100,
                disabled=True,
                help="Preview of your resume text. Click 'Edit Resume Text' to modify."
            )
            # Character count
        char_count = len(st.session_state.raw_resume_text)
        st.caption(f"Characters: {char_count:,}")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
            if st.button("Edit Resume Text", key='edit_resume_btn', help="Open resume text editor"):
                st.session_state.show_resume_modal = True
        
        # Resume text modal
        if st.session_state.get('show_resume_modal', False):
            show_resume_text_modal()

        # Personal Details Section
        st.markdown("## Personal Details (Editable)")
        
        # Full Name field
        full_name_input = st.text_input("Full Name", value=st.session_state.full_name, key='full_name_input')
        st.session_state.full_name = full_name_input

        # Contact and Email
        contact_cols = st.columns(2)
        contact_input = contact_cols[0].text_input("Contact Number", value=st.session_state.contact, key='contact_input')
        email_input = contact_cols[1].text_input("Email Address", value=st.session_state.email, key='email_input')
        st.session_state.contact = contact_input
        st.session_state.email = email_input
        
        # Display the AI-extracted location
        st.caption(f"**AI Extracted Primary Location from Resume:** {st.session_state.extracted_single_location}")
        
    with col_prefs:
        st.subheader("Job Preferences and Targets")

        # Preferred Locations Multi-Select
        st.markdown("**📍 Preferred Locations**")
        
        # Combine standard locations with any custom ones already selected
        current_location_options = list(STANDARD_LOCATIONS)
        for loc in st.session_state.preferred_locations:
            if loc not in current_location_options:
                current_location_options.append(loc)
        
        # Locations Multi-Select (Compact)
        selected_locs = st.multiselect(
            "Select up to 6 target locations: *",
            options=current_location_options,
            default=st.session_state.preferred_locations,
            key='location_select',
            help="**Required** - Select locations where you prefer to work"
        )
        
        # Update session state immediately
        st.session_state.preferred_locations = selected_locs
        
        # Custom location input (compact)
        col1, col2 = st.columns([4, 1])
        with col1:
            custom_location = st.text_input(
                "Add custom location:",
                placeholder="e.g., Custom City",
                key='custom_location_input'
            )
        with col2:
            add_location_clicked = st.button("Add", key='add_location_btn', help="Add custom location")
            
        # Handle location addition
        if add_location_clicked and custom_location and custom_location.strip():
            location = custom_location.strip()
            print(f"TERMINAL: Attempting to add location: {location}")
            if location not in st.session_state.preferred_locations:
                st.session_state.preferred_locations.append(location)
                print(f"TERMINAL: Successfully added location: {location}")
                print(f"TERMINAL: Current locations: {st.session_state.preferred_locations}")
                st.success(f"Added: {location}")
            else:
                print(f"TERMINAL: Location already exists: {location}")
                st.warning("Location already added!")
            st.rerun()

        # Job Targets Multi-Select (Compact)
        st.markdown("**🎯 Target Positions**")
        selected_positions = st.multiselect(
            "Select Target Positions (Max 5):",
            options=STANDARD_POSITIONS,
            default=st.session_state.selected_positions,
            key='position_select',
            help="Select your target job positions"
        )

        # Update positions immediately
        st.session_state.selected_positions = selected_positions

        # Job Types Multi-Select (Compact)
        st.markdown("**💼 Job Types**")
        selected_job_types = st.multiselect(
            "Select preferred job types:",
            options=STANDARD_JOB_TYPES,
            default=st.session_state.selected_job_types,
            key='job_type_select',
            help="Select the types of employment you're interested in"
        )
        
        # Update session state immediately
        st.session_state.selected_job_types = selected_job_types

        # Job Preferences Multi-Select
        st.markdown("**🌐 Job Preference Keywords**")
        
        # Combine standard preferences with any custom ones already selected
        current_preference_options = list(ALL_STANDARD_PREFERENCES)
        for pref in st.session_state.selected_preferences:
            if pref not in current_preference_options:
                current_preference_options.append(pref)
        
        # Job Preferences Multi-Select (Compact)
        selected_prefs = st.multiselect(
            "Select relevant keywords (Work Style, Tech, Domain): *",
            options=current_preference_options,
            default=st.session_state.selected_preferences,
            key='preference_select',
            help="**Required** - Select keywords that describe your job preferences"
        )
        
        # Update session state immediately
        st.session_state.selected_preferences = selected_prefs
        
        # Custom preference input (compact)
        col1, col2 = st.columns([4, 1])
        with col1:
            custom_preference = st.text_input(
                "Add custom preference:",
                placeholder="e.g., Custom Skill",
                key='custom_pref_input_pref'
            )
        with col2:
            add_preference_clicked = st.button("Add", key='add_preference_btn', help="Add custom preference")
            
        # Handle preference addition
        if add_preference_clicked and custom_preference and custom_preference.strip():
            preference = custom_preference.strip()
            print(f"TERMINAL: Attempting to add preference: {preference}")
            if preference not in st.session_state.selected_preferences:
                st.session_state.selected_preferences.append(preference)
                print(f"TERMINAL: Successfully added preference: {preference}")
                print(f"TERMINAL: Current preferences: {st.session_state.selected_preferences}")
                st.success(f"Added: {preference}")
            else:
                print(f"TERMINAL: Preference already exists: {preference}")
                st.warning("Preference already added!")
            st.rerun()

    # Analyze Profile Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Analyze Profile", type="primary", use_container_width=True):
            print("DEBUG: Analyze Profile button clicked!")
            print(f"DEBUG: Current locations before analysis: {st.session_state.preferred_locations}")
            # Validate form before analysis
            if validate_form_before_analysis(st.session_state):
                print("DEBUG: Form validation passed!")
                st.session_state.is_analyzing = True
                st.rerun()
            else:
                print("DEBUG: Form validation failed!")
                st.warning("Please fill in all required fields before analysis.")

    # Show loading overlay when analyzing
    if st.session_state.get('is_analyzing', False):
        print("DEBUG: Starting analysis process...")
        LoadingOverlay.show_loading_overlay()
        
        # Perform the actual analysis
        try:
            # Send data to backend first
            backend_response = send_resume_data_to_backend(st.session_state)
            
            if backend_response:
                st.session_state.backend_data = backend_response
            
            # Continue with local analysis
            data = analyze_resume_logic(
                st.session_state.raw_resume_text, 
                st.session_state.selected_positions, 
                st.session_state.selected_preferences,
                st.session_state.preferred_locations
            )
            
            if data:
                st.session_state.analyzed_data = data
                
                # Update session state with analysis results
                SessionStateManager.update_session_state_from_analysis(data)
                
                print(f"DEBUG: Locations after analysis: {st.session_state.preferred_locations}")
                
                # Print user data to terminal immediately after analysis
                print("DEBUG: About to print user data to terminal...")
                print_ui_data_to_terminal(
                    session_state=st.session_state,
                    analysis_data=data,
                    job_recommendations=None
                )
                print("DEBUG: Finished printing user data to terminal.")

                # Rerun to update the input widgets with new state values
                st.experimental_rerun()
            else:
                st.session_state.analyzed_data = None
    
        except Exception as e:
            st.error(f"Analysis failed: {e}")
        finally:
            # Clear loading state
            st.session_state.is_analyzing = False
            st.rerun()


def job_recommendations_tab():
    """Content for the Job Recommendations tab."""
    st.header("Job Recommendations")
    st.markdown("---")
    
    if st.session_state.get('analyzed_data'):
        DisplayComponents.display_analysis_results(st.session_state.analyzed_data)
        
        # Generate job recommendations
        job_recommendations = generate_job_recommendations(
            resume_text=st.session_state.raw_resume_text,
            target_positions=st.session_state.selected_positions,
            preferences=st.session_state.selected_preferences,
            locations=st.session_state.preferred_locations
        )
        
        # Data was already printed to terminal after analysis completion
        
        # Convert to dict format for display
        job_recommendations_dict = [job.to_dict() for job in job_recommendations]
        
        # Display the recommendations
        DisplayComponents.display_job_recommendations(job_recommendations_dict)
    else:
        st.info("Please run the profile analysis first to see personalized job recommendations.")
        st.markdown("### How it works:")
        st.markdown("1. **Upload your resume** and fill in your preferences")
        st.markdown("2. **Click 'Analyze Profile'** to process your information")
        st.markdown("3. **View personalized job recommendations** based on your skills and experience")
        st.markdown("4. **Click on job titles** to apply directly to positions")


def resume_improver_tab():
    """Content for the Resume Improver tab."""
    st.header("Resume Improvement Suggestions")
    st.markdown("---")
    
    if st.session_state.get('analyzed_data'):
        st.success("✅ Resume analysis completed!")
        
        # Show improvement suggestions
        st.markdown("### AI-Powered Improvement Suggestions")
        
        suggestions = [
            "Add more specific technical skills and certifications",
            "Include quantifiable achievements and metrics",
            "Optimize keywords for ATS (Applicant Tracking Systems)",
            "Highlight relevant project experience",
            "Include industry-specific terminology"
        ]
        
        for i, suggestion in enumerate(suggestions, 1):
            st.write(f"{i}. {suggestion}")
        
        # Show current resume text for editing
        st.markdown("### Edit Your Resume")
        improved_resume = st.text_area(
            "Resume Text (Editable)",
            value=st.session_state.raw_resume_text,
            height=400,
            key='improved_resume_text'
        )
        
        if st.button("💾 Save Improved Resume"):
            st.session_state.raw_resume_text = improved_resume
            st.success("Resume updated successfully!")
    else:
        st.info("Please run the profile analysis first to get improvement suggestions.")


def main():
    """Main application function."""
    # Initialize session state
    SessionStateManager.initialize_session_state()
    
    # Main title
    st.title("🚀 AI Career Optimization Tool")
    st.markdown("**Transform your career with AI-powered resume analysis and job recommendations**")
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "📊 Profile Analysis", 
        "💼 Job Recommendations", 
        "✨ Resume Improver"
    ])

    with tab1:
        profile_analysis_tab()

    with tab2:
        job_recommendations_tab()

    with tab3:
        resume_improver_tab()


if __name__ == "__main__":
    main()