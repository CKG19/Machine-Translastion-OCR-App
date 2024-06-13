import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_navigation_bar import st_navbar
from streamlit_pdf_viewer import pdf_viewer
import pdf2image
import pytesseract
from PIL import Image
import os 
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from db import TranslationApplicationDatabase
from mtl_model import MyMTLModels
from ocr_model import MyOCRModels

class UserInterface:
    def __init__(self, database:TranslationApplicationDatabase, mtlmodel:MyMTLModels, ocrmodel:MyOCRModels):
        self.db = database
        self.mtlmodel = mtlmodel
        self.ocrmodel = ocrmodel
        self.session_state = self._get_session_state()
        self.set_page_config()
        self.menu()

    def set_page_config(self):
        st.set_page_config(page_title="Aplikasi Translasi", initial_sidebar_state="auto", layout="wide")

    def _get_session_state(self):
        if 'authenticated_user' not in st.session_state:
            st.session_state.authenticated_user = None
        return st.session_state

    def menu(self):
        with st.sidebar:
            selected = option_menu(
                menu_title="Main Menu",
                options=[
                    "OCR", 
                    "Translasi", 
                    f"OCR - Translasi",
                    "Admin", 
                ]
            )
        st.sidebar.markdown("---")

        if selected == "OCR": 
            self.ocr()
        elif selected == "Translasi": 
            self.translate()
        elif selected == "OCR - Translasi": 
            self.ocr_translate()    
        elif selected == "Admin":
            self.admin_login_form()   

    def ocr(self):
        # Front End
        st.header("OCR")
        option = st.selectbox('Pilih Model OCR:', ('Tesseract', 'Keras-OCR'), index=None, placeholder='Select')

        # upload file
        uploaded_file = st.file_uploader('', label_visibility='collapsed')

        if uploaded_file:
            file_name = os.path.splitext(uploaded_file.name)[0]
            file_type = os.path.splitext(uploaded_file.name)[1]
        
        if uploaded_file and file_type == ".pdf":
            directory_path = f"C:\\Users\\M-S-I\\Documents\\IBDA Semester 8\\Skripsi\\Web\\pdf2png\\{file_name}"
            os.makedirs(directory_path, exist_ok=True)

            # convert PDF to images
            binary_data = uploaded_file.getvalue()
            images = pdf2image.convert_from_bytes(binary_data)

            all_text = ""
            for i, image in enumerate(images):
                image.reduce(2).save(f"{directory_path}\\page_{i}.png", 'PNG')  

                if option == 'Tesseract':
                    # text = pytesseract.image_to_string(image)
                    text = self.ocrmodel.ocr_with_tesseract(image)
                    all_text += text
                elif option == "Keras-OCR":
                    text = self.ocrmodel.ocr_with_keras(f"{directory_path}\\page_{i}.png")
                    all_text += text
                    
            st.text_area("Extracted Text", value=all_text, height=300)
        
        elif uploaded_file and (file_type == ".jpg" or ".png" or "jpeg"):
            all_text = ""
            with open(f"input_images\\{uploaded_file.name}", "wb") as f:
                f.write(uploaded_file.read())

            if option == 'Tesseract':
                text = pytesseract.image_to_string(Image.open(uploaded_file))
                all_text += text
            elif option == "Keras-OCR":
                text = self.ocrmodel.ocr_with_keras(f"input_images\\{uploaded_file.name}")
                all_text += text
                
            st.text_area("Extracted Text", value=all_text, height=300)

    def translate(self):
        page = st_navbar(["Translasi", "Sejarah Translasi"])
        if page == "Translasi":
            option = st.selectbox('Pilih Model Translasi:', ('MarianMT', 'BART', 'T5'), index=None, placeholder='Select')
            
            # make 2 column to make input and output, horinzontal
            col1, col2 = st.columns(2)
            translation = ""
            with col1:
                src_text = st.text_area("Input:", height=300)
                if option == 'MarianMT':
                    translation = self.mtlmodel.translate_with_marian_mt(src_text)
                    
                elif option == 'BART':
                    translation = self.mtlmodel.translate_with_bart(src_text)

                elif option == 'T5':
                    translation = self.mtlmodel.translate_with_t5(src_text)

            with col2:
                if src_text == "":
                    st.text_area("Output:",  value="", height=300)
                else:
                    st.text_area("Output:", value=translation, height=300)
                    self.db.insert_translation_history(src_text, translation)
        
        else:
            self.translation_history()

    def translation_history(self):
        st.header("Sejarah Translasi")

        # get translation history
        history = self.db.read_translation_history()

        # Check if the user is authenticated as admin
        if self.session_state.authenticated_user == None:
            # st.write(self.authenticated_user)
            for row in history:
                with st.expander(f"Translation ID: {row[0]}", expanded=True):
                    st.text("Input:")
                    st.write(row[1])
                    st.text("Output:")  
                    st.write(row[2])
        else:
            # display editable history
            for row in history:
                with st.expander(f"Translation ID: {row[0]}", expanded=True):
                    st.markdown("""
                    <style>
                    .stTextArea [data-baseweb=base-input] {
                        background-color: #E0E0E0; /* Light gray background */
                    }
                    
                    .stButton>button {
                    margin-right: 5px; /* Adjust the margin between buttons */
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    source_text = st.text_area("", row[1], height=10, key=f"source_{row[0]}", label_visibility='collapsed')
                    translation = st.text_area("", row[2], height=10, key=f"translation_{row[0]}", label_visibility='collapsed')
                    col1, col2 = st.columns([0.05, 1])
                    with col1:
                        if st.button(":pencil2:", key=f"edit_{row[0]}"):
                            self.db.update_translation_history(row[0], source_text, translation)
                            st.rerun()
                    with col2:
                        if st.button(":x:", key=f"delete_{row[0]}"):
                            self.db.delete_translation_history(row[0])
                            st.rerun()

    def ocr_translate(self):
        st.header("OCR - Translasi")
        ocr_model = st.selectbox('Pilih Model OCR:', ('Tesseract', 'Keras-OCR'), index=None, placeholder='Select')
        mtl_model = st.selectbox('Pilih Model Translasi:', ('MarianMT', 'BART', 'T5'), index=None, placeholder='Select')

        # upload file
        uploaded_file = st.file_uploader('Upload file .pdf', type="pdf")

        if uploaded_file:
            file_name = os.path.splitext(uploaded_file.name)[0]
            file_type = os.path.splitext(uploaded_file.name)[1]

        if uploaded_file and file_type == ".pdf":
            directory_path = f"C:\\Users\\M-S-I\\Documents\\IBDA Semester 8\\Skripsi\\Web\\pdf2png\\{file_name}"
            os.makedirs(directory_path, exist_ok=True)

            # Create a new PDF document
            translated_buffer = io.BytesIO()
            translated_doc = SimpleDocTemplate(translated_buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # convert PDF to images
            binary_data = uploaded_file.getvalue()
            images = pdf2image.convert_from_bytes(binary_data)


            for i, image in enumerate(images):
                image.reduce(2).save(f"{directory_path}\\page_{i}.png", 'PNG')

                # ocr
                if ocr_model == 'Tesseract':
                    text = self.ocrmodel.ocr_with_tesseract(image)
                elif ocr_model == 'Keras-OCR':
                    text = self.ocrmodel.ocr_with_keras(f"{directory_path}\\page_{i}.png")

                # translation
                if mtl_model == 'MarianMT':
                    translation = self.mtlmodel.translate_with_marian_mt(text)
                elif mtl_model == 'BART':
                    translation = self.mtlmodel.translate_with_bart(text)
                elif mtl_model == 'T5':
                    translation = self.mtlmodel.translate_with_t5(text)
                

                # Add the translated text to the new page
                elements.append(Paragraph(translation + "\n", styles["BodyText"]))

            # Save the translated document
            translated_doc.build(elements)
            translated_buffer.seek(0)

            # Provide a download button for the translated PDF
            st.download_button(
                label="Download Translated PDF",
                data=translated_buffer,
                file_name=f"translated_{file_name}.pdf",
                mime="application/pdf"
            )
        
    def admin_login_form(self):
        if not self.session_state.authenticated_user:
            st.header("Admin Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if self.login(username, password):
                    self.session_state.authenticated_user = username
                    # st.success(f"Login succesful.\n Welcome {username}")
                    st.rerun
                else:
                    st.error("Incorrect username or password")
                    st.rerun

        else:
            st.header("Admin Logout")
            st.success(f"Login succesful.\n Welcome {self.session_state.authenticated_user.upper()}")
            if st.button("Logout"):
                self.logout() 
                st.rerun()

    def login(self, username, password):
        if self.db.authenticate_admin(username, password):
            return True
        else:
            return False
        
    def logout(self):
        self.session_state.authenticated_user = None
        st.success("Logged out successfully")