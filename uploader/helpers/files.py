import filetype

CONTENT_TYPE_ICO = "image/x-icon"
CONTENT_TYPE_JPG = "image/jpeg"
CONTENT_TYPE_PNG = "image/png"

CONTENT_TYPE_PDF = "application/pdf"
CONTENT_TYPE_UNKNOWN = "application/octet-stream"


def get_content_type(file):
    if hasattr(file, "temporary_file_path"):
        kind = filetype.guess(file.temporary_file_path())
    else:
        kind = filetype.guess(file.read(8192))

    if hasattr(file, "seek") and callable(file.seek):
        file.seek(0)

    return kind.mime if kind else CONTENT_TYPE_UNKNOWN
