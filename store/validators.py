from django.core.exceptions import ValidationError

def validate_file_image(file):
    max_size_kb=50

    if file.size > max_size_kb*1024:
        raise ValidationError(f'The upload fila cannot be more then {max_size_kb} KB!')