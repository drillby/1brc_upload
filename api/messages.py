import enum


class EmailMessages(enum.Enum):
    HEADER = "1BRC - výsledek"
    FOOTER = "Tento email byl vygenerován automaticky."
    SUCCESS = "Váš kód proběhl úspěšně, doba běhu: {runtime:.2f} sekund."
    TIMEOUT = "Váš kód byl přerušen, doba běhu přesáhla {timeout} sekund."
    RUNTIME_ERROR = "Váš kód skončil s chybou: {error}."
    MATCHING_RESULTS = "Na první pohled se zdá, že výstupy jsou stejné."
    DIFFERENT_RESULTS = "Na první pohled se zdá, že výstupy nejsou stejné."
    NEW_LINE = "\n"


class FileUploadMessages(enum.Enum):
    NO_FILE_SELECTED = "Žádný soubor nebyl vybrán."
    WRONG_FILE_FORMAT = "Soubor není v povoleném formátu. Povolené formáty: {formats}"
    SIZE_LIMIT_EXCEEDED = "Soubor je příliš velký. Maximální velikost: {size} MB"
    FILE_UPLOADED = "Soubor nahrán."
    SIZE_LIMIT_WARNING = (
        "Soubor se blíží limitu velikosti. Maximální velikost: {size} MB"
    )


class UserMessages(enum.Enum):
    WRONG_PASSWORD = "Špatné heslo"
    USER_CREATED = "Uživatel vytvořen"
    MISSING_CREDENTIALS = "Chybějící přihlašovací údaje"
    WRONG_EMAIL_DOMAIN = "Špatná doména emailu. Povolené domény: {domains}"


class MessageType(enum.Enum):
    INFORMATION = "information"
    ERROR = "error"
    SUCCESS = "success"
    WARNING = "warning"


class HttpErrorMessages(enum.Enum):
    NOT_FOUND = "Stránka nebyla nalezena."
    INTERNAL_SERVER_ERROR = "Chyba serveru."
    TOO_MANY_REQUESTS = "Příliš mnoho požadavků."
