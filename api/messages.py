import enum


class EmailMessages(enum.Enum):
    HEADER = "1BRC - výsledek"
    FOOTER = "Tento email byl vygenerován automaticky"
    SUCCESS = "Váš kód proběhl úspěšně, doba běhu: {runtime:.2f} sekund"
    TIMEOUT = "Váš kód byl přerušen, doba běhu přesáhla {timeout} sekund"
    RUNTIME_ERROR = "Váš kód skončil s chybou: {error}"


class FileUploadMessages(enum.Enum):
    NO_FILE_SELECTED = "Žádný soubor nebyl vybrán"
    WRONG_FILE_FORMAT = "Soubor musí být ve formátu .py"
    SIZE_LIMIT_EXCEEDED = "Soubor je příliš velký"
    FILE_UPLOADED = "Soubor nahrán"
