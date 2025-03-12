import os
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

def allowed_file(filename, allowed_extensions=None):
    """
    Check if uploaded file has an allowed extension.
    
    Args:
        filename (str): Name of the file to check
        allowed_extensions (set): Set of allowed extensions. If None, uses app config
    
    Returns:
        bool: True if file extension is allowed
    """
    if allowed_extensions is None:
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, subfolder=''):
    """
    Save uploaded file with secure filename.
    
    Args:
        file: FileStorage object
        subfolder (str): Optional subfolder within UPLOAD_FOLDER
    
    Returns:
        str: Path to saved file relative to UPLOAD_FOLDER
    """
    filename = secure_filename(file.filename)
    # Add UUID to filename to ensure uniqueness
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    # Create subfolder if it doesn't exist
    folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(folder_path, exist_ok=True)
    
    file_path = os.path.join(folder_path, unique_filename)
    file.save(file_path)
    
    return os.path.join(subfolder, unique_filename)

def paginate(query, page=1, per_page=None):
    """
    Helper function to paginate SQLAlchemy queries.
    
    Args:
        query: SQLAlchemy query object
        page (int): Page number
        per_page (int): Items per page, defaults to app config
    
    Returns:
        dict: Pagination information and items
    """
    if per_page is None:
        per_page = current_app.config['ITEMS_PER_PAGE']
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': pagination.items,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }