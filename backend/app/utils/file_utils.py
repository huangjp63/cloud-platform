import os


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def get_file_type(extension: str) -> str:
    image_exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
    video_exts = [".mp4", ".avi", ".mkv", ".mov", ".wmv"]
    document_exts = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]
    text_exts = [".txt", ".md", ".json", ".xml", ".csv"]
    archive_exts = [".zip", ".rar", ".7z", ".tar", ".gz"]
    
    ext = extension.lower()
    if ext in image_exts:
        return "image"
    elif ext in video_exts:
        return "video"
    elif ext in document_exts:
        return "document"
    elif ext in text_exts:
        return "text"
    elif ext in archive_exts:
        return "archive"
    else:
        return "other"


def format_file_size(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"
